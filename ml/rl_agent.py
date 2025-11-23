"""
Reinforcement Learning agent for branch-and-price optimization.
Uses PPO (Proximal Policy Optimization) to learn optimal branching strategies.
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
import numpy as np
from typing import List, Dict, Tuple, Optional
from stable_baselines3 import PPO
from stable_baselines3.common.vec_env import DummyVecEnv
from stable_baselines3.common.callbacks import BaseCallback
import gymnasium as gym
from gymnasium import spaces


class BranchingNetwork(nn.Module):
    """
    Neural network for learning branching decisions.
    Takes schedule state and outputs branching scores for rotation variables.
    """
    
    def __init__(self, state_dim: int, hidden_dim: int = 128):
        super(BranchingNetwork, self).__init__()
        
        self.feature_extractor = nn.Sequential(
            nn.Linear(state_dim, hidden_dim),
            nn.ReLU(),
            nn.LayerNorm(hidden_dim),
            nn.Dropout(0.1),
            nn.Linear(hidden_dim, hidden_dim),
            nn.ReLU(),
            nn.LayerNorm(hidden_dim)
        )
        
        self.value_head = nn.Sequential(
            nn.Linear(hidden_dim, hidden_dim // 2),
            nn.ReLU(),
            nn.Linear(hidden_dim // 2, 1)
        )
        
        self.policy_head = nn.Sequential(
            nn.Linear(hidden_dim, hidden_dim // 2),
            nn.ReLU(),
            nn.Linear(hidden_dim // 2, 1)
        )
    
    def forward(self, state):
        features = self.feature_extractor(state)
        value = self.value_head(features)
        policy_logits = self.policy_head(features)
        return policy_logits, value


class SchedulingEnvironment(gym.Env):
    """
    Gym environment for nurse scheduling optimization.
    The agent learns to select which rotation variables to branch on.
    """
    
    def __init__(self, problem_data: Dict, max_iterations: int = 100):
        super(SchedulingEnvironment, self).__init__()
        
        self.problem_data = problem_data
        self.max_iterations = max_iterations
        self.current_iteration = 0
        
        # State space: [LP solution values, dual values, constraint violations, etc.]
        state_dim = 50  # Adjust based on problem size
        self.observation_space = spaces.Box(
            low=-np.inf, high=np.inf, shape=(state_dim,), dtype=np.float32
        )
        
        # Action space: Select which variable to branch on
        max_variables = 100  # Maximum number of rotation variables
        self.action_space = spaces.Discrete(max_variables)
        
        # Current state
        self.current_state = None
        self.current_solution_quality = 0.0
        self.best_solution_quality = float('inf')
        
        # Reset environment
        self.reset()
    
    def reset(self, seed=None, options=None):
        """Reset the environment"""
        super().reset(seed=seed)
        
        self.current_iteration = 0
        self.current_solution_quality = float('inf')
        self.best_solution_quality = float('inf')
        
        # Initialize state
        self.current_state = self._get_initial_state()
        
        return self.current_state, {}
    
    def _get_initial_state(self) -> np.ndarray:
        """Get initial state representation"""
        # This would extract features from the current LP relaxation
        state = np.zeros(self.observation_space.shape[0], dtype=np.float32)
        
        # Features could include:
        # - Fractionality of variables (how far from integer)
        # - Dual values (importance of constraints)
        # - Reduced costs
        # - Problem structure features
        # - Historical performance features
        
        return state
    
    def _extract_state_features(self, lp_solution: Dict, 
                                dual_values: Dict) -> np.ndarray:
        """
        Extract state features from current LP solution.
        
        Features:
        1. Variable fractionality metrics
        2. Dual value statistics
        3. Constraint violation metrics
        4. Progress indicators
        5. Problem-specific features
        """
        features = []
        
        # Fractionality features
        if 'variables' in lp_solution:
            values = list(lp_solution['variables'].values())
            fractionalities = [abs(v - round(v)) for v in values]
            
            features.extend([
                np.mean(fractionalities) if fractionalities else 0,
                np.max(fractionalities) if fractionalities else 0,
                np.std(fractionalities) if fractionalities else 0,
                sum(1 for f in fractionalities if f > 0.1) / (len(fractionalities) + 1e-6)
            ])
        else:
            features.extend([0, 0, 0, 0])
        
        # Dual value features
        if 'duals' in dual_values:
            duals = list(dual_values['duals'].values())
            features.extend([
                np.mean(np.abs(duals)) if duals else 0,
                np.max(np.abs(duals)) if duals else 0,
                np.std(duals) if duals else 0
            ])
        else:
            features.extend([0, 0, 0])
        
        # Solution quality
        features.append(lp_solution.get('objective', 0) / 1000)  # Normalized
        
        # Iteration progress
        features.append(self.current_iteration / self.max_iterations)
        
        # Gap to best solution
        gap = (self.current_solution_quality - self.best_solution_quality) / \
              (self.best_solution_quality + 1e-6)
        features.append(max(-1, min(1, gap)))
        
        # Pad to required dimension
        state = np.array(features, dtype=np.float32)
        if len(state) < self.observation_space.shape[0]:
            state = np.pad(state, (0, self.observation_space.shape[0] - len(state)))
        
        return state[:self.observation_space.shape[0]]
    
    def step(self, action: int):
        """
        Take a step in the environment by selecting a branching variable.
        
        Args:
            action: Index of variable to branch on
        
        Returns:
            observation, reward, terminated, truncated, info
        """
        self.current_iteration += 1
        
        # Simulate branching decision
        # In real implementation, this would:
        # 1. Branch on selected variable
        # 2. Solve resulting subproblems
        # 3. Update solution quality
        
        # For now, simulate improvement
        improvement = np.random.random() * 0.1
        new_quality = self.current_solution_quality * (1 - improvement)
        
        # Calculate reward
        reward = self._calculate_reward(new_quality, action)
        
        # Update state
        self.current_solution_quality = new_quality
        self.best_solution_quality = min(self.best_solution_quality, new_quality)
        
        # Generate new state (would come from LP solution)
        self.current_state = self._get_initial_state()
        
        # Check termination
        terminated = self.current_iteration >= self.max_iterations
        truncated = False
        
        info = {
            'solution_quality': self.current_solution_quality,
            'best_quality': self.best_solution_quality,
            'iteration': self.current_iteration
        }
        
        return self.current_state, reward, terminated, truncated, info
    
    def _calculate_reward(self, new_quality: float, action: int) -> float:
        """
        Calculate reward for the branching decision.
        
        Reward components:
        1. Solution improvement
        2. Speed (fewer iterations better)
        3. Quality relative to best known
        """
        # Improvement reward
        improvement = max(0, self.current_solution_quality - new_quality)
        improvement_reward = improvement * 100
        
        # Speed penalty (encourage fewer iterations)
        speed_penalty = -0.1
        
        # Quality bonus if near best
        gap_to_best = (new_quality - self.best_solution_quality) / \
                     (self.best_solution_quality + 1e-6)
        quality_bonus = 10 if gap_to_best < 0.01 else 0
        
        total_reward = improvement_reward + speed_penalty + quality_bonus
        
        return total_reward
    
    def render(self, mode='human'):
        """Render the environment state"""
        print(f"Iteration: {self.current_iteration}/{self.max_iterations}")
        print(f"Current Quality: {self.current_solution_quality:.2f}")
        print(f"Best Quality: {self.best_solution_quality:.2f}")


class RLBranchingAgent:
    """
    RL agent for learning optimal branching strategies in branch-and-price.
    """
    
    def __init__(self, environment: SchedulingEnvironment):
        self.env = DummyVecEnv([lambda: environment])
        
        # PPO agent
        self.agent = PPO(
            "MlpPolicy",
            self.env,
            learning_rate=3e-4,
            n_steps=2048,
            batch_size=64,
            n_epochs=10,
            gamma=0.99,
            gae_lambda=0.95,
            clip_range=0.2,
            verbose=1,
            tensorboard_log="./tensorboard_logs/"
        )
        
        self.is_trained = False
    
    def train(self, total_timesteps: int = 100000, 
             callback: Optional[BaseCallback] = None):
        """
        Train the RL agent.
        
        Args:
            total_timesteps: Total number of environment steps
            callback: Optional callback for monitoring
        """
        print("Training RL branching agent...")
        
        self.agent.learn(
            total_timesteps=total_timesteps,
            callback=callback,
            progress_bar=True
        )
        
        self.is_trained = True
        print("Training completed!")
    
    def select_branching_variable(self, state: np.ndarray) -> int:
        """
        Select which variable to branch on given current state.
        
        Args:
            state: Current LP solution state
        
        Returns:
            Index of variable to branch on
        """
        if not self.is_trained:
            # Random selection if not trained
            return np.random.randint(0, self.env.envs[0].action_space.n)
        
        action, _ = self.agent.predict(state, deterministic=True)
        return int(action)
    
    def save(self, path: str):
        """Save the trained agent"""
        if not self.is_trained:
            raise ValueError("Cannot save untrained agent")
        
        self.agent.save(path)
        print(f"Agent saved to {path}")
    
    def load(self, path: str):
        """Load a trained agent"""
        self.agent = PPO.load(path, env=self.env)
        self.is_trained = True
        print(f"Agent loaded from {path}")


class TrainingCallback(BaseCallback):
    """Callback for monitoring training progress"""
    
    def __init__(self, check_freq: int = 1000, verbose: int = 1):
        super(TrainingCallback, self).__init__(verbose)
        self.check_freq = check_freq
        self.best_mean_reward = -np.inf
    
    def _on_step(self) -> bool:
        if self.n_calls % self.check_freq == 0:
            # Calculate mean reward
            if len(self.model.ep_info_buffer) > 0:
                mean_reward = np.mean([ep_info['r'] for ep_info in self.model.ep_info_buffer])
                
                if self.verbose > 0:
                    print(f"Steps: {self.num_timesteps}, Mean Reward: {mean_reward:.2f}")
                
                # Save if best
                if mean_reward > self.best_mean_reward:
                    self.best_mean_reward = mean_reward
                    if self.verbose > 0:
                        print(f"New best mean reward: {mean_reward:.2f}")
        
        return True


def create_training_problems(num_problems: int = 100) -> List[Dict]:
    """Generate synthetic scheduling problems for training"""
    problems = []
    
    for i in range(num_problems):
        problem = {
            'num_nurses': np.random.randint(20, 50),
            'num_days': np.random.randint(7, 28),
            'num_shifts': np.random.randint(3, 5),
            'complexity': np.random.random()
        }
        problems.append(problem)
    
    return problems


if __name__ == "__main__":
    print("Creating training environment...")
    
    # Create a sample problem
    sample_problem = {
        'num_nurses': 30,
        'num_days': 14,
        'num_shifts': 3
    }
    
    env = SchedulingEnvironment(sample_problem, max_iterations=50)
    
    print("Initializing RL agent...")
    agent = RLBranchingAgent(env)
    
    print("Training agent...")
    callback = TrainingCallback(check_freq=500)
    agent.train(total_timesteps=10000, callback=callback)
    
    print("\nTesting trained agent...")
    obs = env.reset()[0]
    for i in range(10):
        action = agent.select_branching_variable(obs)
        obs, reward, done, truncated, info = env.step(action)
        print(f"Step {i+1}: Action={action}, Reward={reward:.2f}, Quality={info['solution_quality']:.2f}")
        
        if done or truncated:
            break
    
    print("\nSaving agent...")
    agent.save("rl_branching_agent")
    
    print("\nRL agent training completed!")
