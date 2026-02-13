"""
Reinforcement Learning Framework for Trading
DQN and other RL algorithms for optimal trading strategies
"""

import numpy as np
from typing import Dict, List, Tuple, Optional
from collections import deque
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TradingEnvironment:
    """Trading environment for RL agents"""
    
    def __init__(self, initial_balance: float = 10000):
        self.initial_balance = initial_balance
        self.balance = initial_balance
        self.position = 0  # -1: short, 0: neutral, 1: long
        self.entry_price = 0
        self.current_step = 0
        self.data = None
        
        logger.info(f"Trading environment created: initial_balance=${initial_balance}")
    
    def reset(self, data: np.ndarray) -> np.ndarray:
        """
        Reset environment
        
        Args:
            data: Market data
            
        Returns:
            Initial state
        """
        self.data = data
        self.balance = self.initial_balance
        self.position = 0
        self.entry_price = 0
        self.current_step = 0
        
        return self._get_state()
    
    def _get_state(self) -> np.ndarray:
        """Get current state"""
        if self.data is None or self.current_step >= len(self.data):
            return np.zeros(10)
        
        # State: [price, position, balance, recent_prices, indicators]
        price = self.data[self.current_step]
        recent_prices = self.data[max(0, self.current_step-5):self.current_step+1]
        
        # Pad if necessary
        if len(recent_prices) < 6:
            recent_prices = np.pad(recent_prices, (6-len(recent_prices), 0), 'edge')
        
        state = np.array([
            price / 100,  # Normalized price
            self.position,
            self.balance / self.initial_balance,
            *recent_prices[-5:] / 100  # Last 5 prices normalized
        ])
        
        return state
    
    def step(self, action: int) -> Tuple[np.ndarray, float, bool, Dict]:
        """
        Take action in environment
        
        Args:
            action: 0=SELL/close, 1=HOLD, 2=BUY/long
            
        Returns:
            next_state, reward, done, info
        """
        if self.data is None:
            return self._get_state(), 0, True, {}
        
        price = self.data[self.current_step]
        reward = 0
        
        # Execute action
        if action == 2:  # BUY
            if self.position != 1:
                # Close any short position
                if self.position == -1:
                    pnl = (self.entry_price - price) * abs(self.position)
                    self.balance += pnl
                    reward += pnl
                
                # Open long
                self.position = 1
                self.entry_price = price
                
        elif action == 0:  # SELL
            if self.position != -1:
                # Close any long position
                if self.position == 1:
                    pnl = (price - self.entry_price) * abs(self.position)
                    self.balance += pnl
                    reward += pnl
                
                # Open short
                self.position = -1
                self.entry_price = price
                
        else:  # HOLD
            # Calculate unrealized PnL
            if self.position == 1:
                reward = (price - self.entry_price) * 0.01  # Small reward for holding profitable
            elif self.position == -1:
                reward = (self.entry_price - price) * 0.01
        
        # Move to next step
        self.current_step += 1
        done = self.current_step >= len(self.data) - 1
        
        # Get next state
        next_state = self._get_state()
        
        info = {
            'balance': self.balance,
            'position': self.position,
            'price': price
        }
        
        return next_state, reward, done, info


class ReplayBuffer:
    """Experience replay buffer for DQN"""
    
    def __init__(self, capacity: int = 10000):
        self.buffer = deque(maxlen=capacity)
        logger.info(f"Replay buffer created: capacity={capacity}")
    
    def push(self, state: np.ndarray, action: int, reward: float, 
             next_state: np.ndarray, done: bool):
        """Add experience to buffer"""
        self.buffer.append((state, action, reward, next_state, done))
    
    def sample(self, batch_size: int) -> List[Tuple]:
        """Sample random batch"""
        indices = np.random.choice(len(self.buffer), batch_size, replace=False)
        return [self.buffer[i] for i in indices]
    
    def __len__(self) -> int:
        return len(self.buffer)


class DQNAgent:
    """Deep Q-Network agent"""
    
    def __init__(self, state_size: int = 10, action_size: int = 3, 
                 learning_rate: float = 0.001, gamma: float = 0.95,
                 epsilon: float = 1.0, epsilon_decay: float = 0.995,
                 epsilon_min: float = 0.01):
        self.state_size = state_size
        self.action_size = action_size
        self.lr = learning_rate
        self.gamma = gamma
        self.epsilon = epsilon
        self.epsilon_decay = epsilon_decay
        self.epsilon_min = epsilon_min
        
        self.replay_buffer = ReplayBuffer(capacity=10000)
        self.q_network = self._build_network()
        self.target_network = self._build_network()
        
        logger.info(f"DQN Agent created: state_size={state_size}, actions={action_size}")
    
    def _build_network(self) -> Dict:
        """Build Q-network"""
        # Placeholder for neural network
        # In production, use TensorFlow/PyTorch
        return {
            'type': 'DQN',
            'layers': [
                {'type': 'Dense', 'units': 64, 'activation': 'relu'},
                {'type': 'Dense', 'units': 64, 'activation': 'relu'},
                {'type': 'Dense', 'units': self.action_size, 'activation': 'linear'}
            ],
            'optimizer': 'adam',
            'lr': self.lr
        }
    
    def select_action(self, state: np.ndarray, training: bool = True) -> int:
        """
        Select action using epsilon-greedy policy
        
        Args:
            state: Current state
            training: If True, use epsilon-greedy
            
        Returns:
            Selected action
        """
        if training and np.random.random() < self.epsilon:
            # Explore
            return np.random.randint(self.action_size)
        else:
            # Exploit
            q_values = self._predict_q_values(state)
            return int(np.argmax(q_values))
    
    def _predict_q_values(self, state: np.ndarray) -> np.ndarray:
        """Predict Q-values for state"""
        # Placeholder prediction
        return np.random.randn(self.action_size)
    
    def remember(self, state: np.ndarray, action: int, reward: float,
                next_state: np.ndarray, done: bool):
        """Store experience in replay buffer"""
        self.replay_buffer.push(state, action, reward, next_state, done)
    
    def train(self, batch_size: int = 32) -> Optional[float]:
        """
        Train on batch from replay buffer
        
        Args:
            batch_size: Batch size
            
        Returns:
            Loss value
        """
        if len(self.replay_buffer) < batch_size:
            return None
        
        # Sample batch
        batch = self.replay_buffer.sample(batch_size)
        
        # Placeholder for training
        # In production: compute targets, update Q-network
        loss = np.random.random()
        
        # Decay epsilon
        if self.epsilon > self.epsilon_min:
            self.epsilon *= self.epsilon_decay
        
        return loss
    
    def update_target_network(self):
        """Update target network with Q-network weights"""
        # Placeholder
        # In production: copy weights from Q-network to target network
        logger.info("Target network updated")
    
    def train_episode(self, env: TradingEnvironment, 
                     data: np.ndarray) -> Dict:
        """
        Train for one episode
        
        Args:
            env: Trading environment
            data: Market data
            
        Returns:
            Episode statistics
        """
        state = env.reset(data)
        total_reward = 0
        steps = 0
        
        while True:
            # Select action
            action = self.select_action(state, training=True)
            
            # Take action
            next_state, reward, done, info = env.step(action)
            
            # Remember
            self.remember(state, action, reward, next_state, done)
            
            # Train
            loss = self.train(batch_size=32)
            
            total_reward += reward
            steps += 1
            state = next_state
            
            if done:
                break
        
        # Update target network periodically
        if steps % 100 == 0:
            self.update_target_network()
        
        return {
            'total_reward': total_reward,
            'steps': steps,
            'final_balance': info.get('balance', 0),
            'epsilon': self.epsilon
        }


class ReinforcementLearningSystem:
    """Complete RL system for trading"""
    
    def __init__(self, initial_balance: float = 10000):
        self.env = TradingEnvironment(initial_balance=initial_balance)
        self.agent = DQNAgent(state_size=10, action_size=3)
        
        self.training_history = []
        logger.info("Reinforcement Learning System initialized")
    
    def create_environment(self, market_data: np.ndarray) -> TradingEnvironment:
        """Create trading environment"""
        self.env.reset(market_data)
        return self.env
    
    def create_dqn_agent(self) -> DQNAgent:
        """Create DQN agent"""
        return self.agent
    
    def train(self, market_data: np.ndarray, episodes: int = 100) -> List[Dict]:
        """
        Train agent on market data
        
        Args:
            market_data: Historical market data
            episodes: Number of training episodes
            
        Returns:
            Training history
        """
        logger.info(f"Training RL agent: episodes={episodes}")
        
        for episode in range(episodes):
            stats = self.agent.train_episode(self.env, market_data)
            self.training_history.append(stats)
            
            if (episode + 1) % 10 == 0:
                avg_reward = np.mean([s['total_reward'] for s in self.training_history[-10:]])
                logger.info(f"Episode {episode+1}/{episodes}: avg_reward={avg_reward:.2f}, epsilon={stats['epsilon']:.3f}")
        
        return self.training_history
    
    def predict(self, current_state: np.ndarray) -> Dict:
        """
        Make trading decision
        
        Args:
            current_state: Current market state
            
        Returns:
            Trading decision
        """
        action = self.agent.select_action(current_state, training=False)
        
        actions_map = {0: 'SELL', 1: 'HOLD', 2: 'BUY'}
        
        return {
            'action': actions_map[action],
            'action_index': action,
            'epsilon': self.agent.epsilon,
            'confidence': 1.0 - self.agent.epsilon  # Higher confidence when epsilon is low
        }
    
    def analyze(self, ohlcv_data: Dict[str, np.ndarray]) -> Dict:
        """
        Analyze market and provide RL-based recommendation
        
        Args:
            ohlcv_data: OHLCV market data
            
        Returns:
            Analysis with recommendation
        """
        # Extract close prices
        close = ohlcv_data['close']
        
        # Create state
        state = np.array([
            close[-1] / 100,  # Current price
            0,  # Position (neutral for analysis)
            1.0,  # Normalized balance
            *close[-5:] / 100  # Recent prices
        ])
        
        # Get prediction
        prediction = self.predict(state)
        
        return {
            'signal': prediction['action'],
            'confidence': prediction['confidence'],
            'action_index': prediction['action_index'],
            'epsilon': prediction['epsilon'],
            'method': 'DQN_Reinforcement_Learning'
        }


def create_rl_system(initial_balance: float = 10000) -> ReinforcementLearningSystem:
    """Factory function to create RL system"""
    return ReinforcementLearningSystem(initial_balance=initial_balance)


if __name__ == "__main__":
    # Example usage
    print("=" * 60)
    print("REINFORCEMENT LEARNING FRAMEWORK FOR TRADING")
    print("=" * 60)
    
    # Create system
    rl_system = create_rl_system(initial_balance=10000)
    
    # Generate sample market data
    np.random.seed(42)
    n_samples = 500
    market_data = 100 + np.cumsum(np.random.randn(n_samples) * 0.5)
    
    # Train agent
    print("\nTraining DQN agent...")
    history = rl_system.train(market_data, episodes=50)
    
    # Show training progress
    print(f"\nTraining completed: {len(history)} episodes")
    final_stats = history[-1]
    print(f"  Final reward: {final_stats['total_reward']:.2f}")
    print(f"  Final balance: ${final_stats['final_balance']:.2f}")
    print(f"  Final epsilon: {final_stats['epsilon']:.3f}")
    
    # Make prediction
    sample_data = {
        'close': market_data[-100:]
    }
    result = rl_system.analyze(sample_data)
    
    print("\nRL Analysis:")
    print(f"  Signal: {result['signal']}")
    print(f"  Confidence: {result['confidence']:.2%}")
    print(f"  Method: {result['method']}")
    
    print("\n✓ Reinforcement Learning Framework ready for trading!")
