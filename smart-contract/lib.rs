#![cfg_attr(not(feature = "std"), no_std, no_main)]

#[ink::contract]
mod polka_agents {
    use ink::storage::Mapping;
    use ink::prelude::vec::Vec;
    use ink::prelude::string::String;

    // Type aliases
    pub type AgentId = u32;
    pub type InteractionId = u64;

    #[derive(Debug, scale::Encode, scale::Decode, PartialEq, Eq, Clone)]
    #[cfg_attr(feature = "std", derive(scale_info::TypeInfo))]
    pub enum AgentType {
        Chatbot,
        Translation,
        Sentiment,
        Summarization,
        JobApplication,
    }

    #[derive(Debug, scale::Encode, scale::Decode, PartialEq, Eq, Clone)]
    #[cfg_attr(feature = "std", derive(scale_info::TypeInfo))]
    pub struct AgentMetadata {
        name: String,
        description: String,
        agent_type: AgentType,
        model_info: String,
    }

    #[derive(Debug, scale::Encode, scale::Decode, PartialEq, Eq, Clone)]
    #[cfg_attr(feature = "std", derive(scale_info::TypeInfo))]
    pub enum InteractionStatus {
        Pending,
        Completed,
        Failed,
    }

    #[derive(Debug, scale::Encode, scale::Decode, PartialEq, Eq, Clone)]
    #[cfg_attr(feature = "std", derive(scale_info::TypeInfo))]
    pub struct Interaction {
        id: InteractionId,
        agent_id: AgentId,
        user: AccountId,
        query_data: Vec<u8>,
        response_data: Option<Vec<u8>>,
        timestamp: u64,
        status: InteractionStatus,
        fee_paid: Balance,
    }

    #[derive(Debug, scale::Encode, scale::Decode, PartialEq, Eq)]
    #[cfg_attr(feature = "std", derive(scale_info::TypeInfo))]
    pub enum Error {
        AgentNotFound,
        AgentAlreadyExists,
        AgentNotActive,
        UnauthorizedOwner,
        InsufficientPayment,
        InteractionNotFound,
        InvalidStakeAmount,
        InvalidFeePercentage,
    }

    #[ink(storage)]
    pub struct PolkaAgents {
        agent_counter: AgentId,
        interaction_counter: InteractionId,
        
        // Registry of all AI agents
        agents: Mapping<AgentId, Agent>,
        
        // Record of interactions
        interactions: Mapping<InteractionId, Interaction>,
        
        // User interactions
        user_interactions: Mapping<AccountId, Vec<InteractionId>>,
        
        // Agent interactions
        agent_interactions: Mapping<AgentId, Vec<InteractionId>>,
        
        // Fee configuration
        platform_fee_percentage: u8,
        
        // Platform owner
        owner: AccountId,
    }

    #[derive(Debug, scale::Encode, scale::Decode, PartialEq, Eq, Clone)]
    #[cfg_attr(feature = "std", derive(scale_info::TypeInfo))]
    pub struct Agent {
        id: AgentId,
        owner: AccountId,
        metadata: AgentMetadata,
        price_per_query: Balance,
        stake_amount: Balance,
        active: bool,
        created_at: u64,
    }

    impl PolkaAgents {
        #[ink(constructor)]
        pub fn new(platform_fee_percentage: u8) -> Self {
            let owner = Self::env().caller();
            
            // Validate fee percentage (must be between 0 and 100)
            assert!(platform_fee_percentage <= 100, "Fee percentage must be between 0 and 100");
            
            Self {
                agent_counter: 1,  // Start from 1
                interaction_counter: 1,
                agents: Mapping::default(),
                interactions: Mapping::default(),
                user_interactions: Mapping::default(),
                agent_interactions: Mapping::default(),
                platform_fee_percentage,
                owner,
            }
        }

        /// Register a new AI agent
        #[ink(message, payable)]
        pub fn register_agent(
            &mut self,
            metadata: AgentMetadata,
            price_per_query: Balance,
        ) -> Result<AgentId, Error> {
            let caller = self.env().caller();
            let stake_amount = self.env().transferred_value();
            
            // Ensure minimum stake amount (can be adjusted)
            if stake_amount < 10 {
                return Err(Error::InvalidStakeAmount);
            }
            
            let agent_id = self.agent_counter;
            self.agent_counter += 1;
            
            let current_time = self.env().block_timestamp();
            
            // Create new agent
            let agent = Agent {
                id: agent_id,
                owner: caller,
                metadata,
                price_per_query,
                stake_amount,
                active: true,
                created_at: current_time,
            };
            
            // Store the agent
            self.agents.insert(agent_id, &agent);
            
            // Emit event
            self.env().emit_event(AgentRegistered {
                agent_id,
                owner: caller,
                price_per_query,
                stake_amount,
            });
            
            Ok(agent_id)
        }

        /// Update agent information
        #[ink(message)]
        pub fn update_agent(
            &mut self,
            agent_id: AgentId,
            metadata: Option<AgentMetadata>,
            price_per_query: Option<Balance>,
            active: Option<bool>,
        ) -> Result<(), Error> {
            let caller = self.env().caller();
            
            // Get the agent, return error if not found
            let mut agent = self.agents.get(agent_id).ok_or(Error::AgentNotFound)?;
            
            // Check if caller is the owner
            if agent.owner != caller {
                return Err(Error::UnauthorizedOwner);
            }
            
            // Update fields if provided
            if let Some(new_metadata) = metadata {
                agent.metadata = new_metadata;
            }
            
            if let Some(new_price) = price_per_query {
                agent.price_per_query = new_price;
            }
            
            if let Some(new_active) = active {
                agent.active = new_active;
            }
            
            // Store updated agent
            self.agents.insert(agent_id, &agent);
            
            // Emit event
            self.env().emit_event(AgentUpdated {
                agent_id,
                owner: caller,
            });
            
            Ok(())
        }

        /// Get agent information
        #[ink(message)]
        pub fn get_agent(&self, agent_id: AgentId) -> Option<Agent> {
            self.agents.get(agent_id)
        }

        /// Query an agent (pay fee)
        #[ink(message, payable)]
        pub fn query_agent(
            &mut self,
            agent_id: AgentId,
            query_data: Vec<u8>,
        ) -> Result<InteractionId, Error> {
            let caller = self.env().caller();
            let payment = self.env().transferred_value();
            
            // Get the agent, return error if not found
            let agent = self.agents.get(agent_id).ok_or(Error::AgentNotFound)?;
            
            // Check if agent is active
            if !agent.active {
                return Err(Error::AgentNotActive);
            }
            
            // Check if payment is sufficient
            if payment < agent.price_per_query {
                return Err(Error::InsufficientPayment);
            }
            
            // Calculate platform fee
            let platform_fee = payment * self.platform_fee_percentage as u128 / 100;
            let agent_fee = payment - platform_fee;
            
            // Transfer fee to agent owner (minus platform fee)
            if agent_fee > 0 {
                if self.env().transfer(agent.owner, agent_fee).is_err() {
                    // Handle transfer error (in a real implementation)
                    // For simplicity, we continue anyway
                }
            }
            
            // Generate interaction ID
            let interaction_id = self.interaction_counter;
            self.interaction_counter += 1;
            
            let current_time = self.env().block_timestamp();
            
            // Create interaction record
            let interaction = Interaction {
                id: interaction_id,
                agent_id,
                user: caller,
                query_data,
                response_data: None,
                timestamp: current_time,
                status: InteractionStatus::Pending,
                fee_paid: payment,
            };
            
            // Store the interaction
            self.interactions.insert(interaction_id, &interaction);
            
            // Update user interactions
            let mut user_interactions = self.user_interactions.get(caller).unwrap_or_default();
            user_interactions.push(interaction_id);
            self.user_interactions.insert(caller, &user_interactions);
            
            // Update agent interactions
            let mut agent_interactions = self.agent_interactions.get(agent_id).unwrap_or_default();
            agent_interactions.push(interaction_id);
            self.agent_interactions.insert(agent_id, &agent_interactions);
            
            // Emit event
            self.env().emit_event(QuerySubmitted {
                interaction_id,
                agent_id,
                user: caller,
                fee_paid: payment,
            });
            
            Ok(interaction_id)
        }

        /// Submit response to a query
        #[ink(message)]
        pub fn submit_response(
            &mut self,
            interaction_id: InteractionId,
            response_data: Vec<u8>,
        ) -> Result<(), Error> {
            let caller = self.env().caller();
            
            // Get the interaction
            let mut interaction = self.interactions.get(interaction_id).ok_or(Error::InteractionNotFound)?;
            
            // Get the agent
            let agent = self.agents.get(interaction.agent_id).ok_or(Error::AgentNotFound)?;
            
            // Check if caller is the agent owner
            if agent.owner != caller {
                return Err(Error::UnauthorizedOwner);
            }
            
            // Update interaction with response
            interaction.response_data = Some(response_data);
            interaction.status = InteractionStatus::Completed;
            
            // Store updated interaction
            self.interactions.insert(interaction_id, &interaction);
            
            // Emit event
            self.env().emit_event(ResponseSubmitted {
                interaction_id,
                agent_id: interaction.agent_id,
                user: interaction.user,
            });
            
            Ok(())
        }

        /// Get an interaction
        #[ink(message)]
        pub fn get_interaction(&self, interaction_id: InteractionId) -> Option<Interaction> {
            self.interactions.get(interaction_id)
        }

        /// Get user interactions
        #[ink(message)]
        pub fn get_user_interactions(&self, user: AccountId) -> Vec<InteractionId> {
            self.user_interactions.get(user).unwrap_or_default()
        }

        /// Get agent interactions
        #[ink(message)]
        pub fn get_agent_interactions(&self, agent_id: AgentId) -> Vec<InteractionId> {
            self.agent_interactions.get(agent_id).unwrap_or_default()
        }

        /// Update platform fee percentage
        #[ink(message)]
        pub fn update_platform_fee(&mut self, new_fee_percentage: u8) -> Result<(), Error> {
            let caller = self.env().caller();
            
            // Check if caller is the owner
            if caller != self.owner {
                return Err(Error::UnauthorizedOwner);
            }
            
            // Validate fee percentage
            if new_fee_percentage > 100 {
                return Err(Error::InvalidFeePercentage);
            }
            
            // Update fee
            self.platform_fee_percentage = new_fee_percentage;
            
            Ok(())
        }

        /// Withdraw stake (deactivate agent)
        #[ink(message)]
        pub fn withdraw_stake(&mut self, agent_id: AgentId) -> Result<(), Error> {
            let caller = self.env().caller();
            
            // Get the agent
            let mut agent = self.agents.get(agent_id).ok_or(Error::AgentNotFound)?;
            
            // Check if caller is the owner
            if agent.owner != caller {
                return Err(Error::UnauthorizedOwner);
            }
            
            // Deactivate agent
            agent.active = false;
            
            // Transfer stake back to owner
            if agent.stake_amount > 0 {
                let stake = agent.stake_amount;
                agent.stake_amount = 0;
                
                if self.env().transfer(caller, stake).is_err() {
                    // Handle transfer error
                    // For simplicity, we continue anyway
                }
            }
            
            // Update agent
            self.agents.insert(agent_id, &agent);
            
            // Emit event
            self.env().emit_event(StakeWithdrawn {
                agent_id,
                owner: caller,
            });
            
            Ok(())
        }
    }

    // Events
    #[ink(event)]
    pub struct AgentRegistered {
        #[ink(topic)]
        agent_id: AgentId,
        #[ink(topic)]
        owner: AccountId,
        price_per_query: Balance,
        stake_amount: Balance,
    }

    #[ink(event)]
    pub struct AgentUpdated {
        #[ink(topic)]
        agent_id: AgentId,
        #[ink(topic)]
        owner: AccountId,
    }

    #[ink(event)]
    pub struct QuerySubmitted {
        #[ink(topic)]
        interaction_id: InteractionId,
        #[ink(topic)]
        agent_id: AgentId,
        #[ink(topic)]
        user: AccountId,
        fee_paid: Balance,
    }

    #[ink(event)]
    pub struct ResponseSubmitted {
        #[ink(topic)]
        interaction_id: InteractionId,
        #[ink(topic)]
        agent_id: AgentId,
        #[ink(topic)]
        user: AccountId,
    }

    #[ink(event)]
    pub struct StakeWithdrawn {
        #[ink(topic)]
        agent_id: AgentId,
        #[ink(topic)]
        owner: AccountId,
    }

    // Unit tests are omitted for brevity
}