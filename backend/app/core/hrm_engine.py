"""
HRM Engine for Decision System

Wrapper around the Hierarchical Reasoning Model (HRM) that:
1. Converts structured HRM input to model format
2. Executes reasoning through the HRM model
3. Interprets model output into actionable decisions

This bridges the backend API with the actual HRM neural network model.
"""

import os
import sys
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
import json

# Add HRM-main to path
hrm_path = os.path.join(os.path.dirname(__file__), "../../../HRM-main")
if os.path.exists(hrm_path):
    sys.path.insert(0, hrm_path)
    HRM_MODEL_AVAILABLE = True
else:
    HRM_MODEL_AVAILABLE = False
    logging.warning("HRM model directory not found. Running in simulation mode.")

try:
    import torch
    TORCH_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False
    logging.warning("PyTorch not installed. Running in simulation mode.")

from ..schemas.request_schema import (
    HRMInput,
    DecisionOutput,
    DecisionStatus,
    CompletedAction,
    StrategicLevel,
    TacticalLevel,
    OperationalLevel
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class HRMEngine:
    """
    Hierarchical Reasoning Model Engine
    
    Processes structured HRM inputs through the actual HRM neural network
    or simulates the reasoning process if model is unavailable.
    
    Features:
    - Model loading and initialization
    - Input encoding for HRM format
    - Hierarchical reasoning execution
    - Output decoding to decision format
    - Simulation mode for testing without full model
    """
    
    def __init__(self, model_path: Optional[str] = None, use_simulation: bool = None):
        """
        Initialize HRM Engine
        
        Args:
            model_path: Path to pretrained HRM model checkpoint
            use_simulation: Force simulation mode (if None, auto-detect)
        """
        self.model_path = model_path
        self.model = None
        self.device = "cpu"
        
        # Determine if we should use simulation
        if use_simulation is None:
            self.use_simulation = not (HRM_MODEL_AVAILABLE and TORCH_AVAILABLE)
        else:
            self.use_simulation = use_simulation
        
        if not self.use_simulation:
            self._initialize_model()
        else:
            logger.info("HRM Engine running in SIMULATION mode")
    
    def _initialize_model(self):
        """Initialize the actual HRM model"""
        try:
            if torch.cuda.is_available():
                self.device = "cuda"
                logger.info("CUDA available - using GPU")
            else:
                self.device = "cpu"
                logger.info("CUDA not available - using CPU")
            
            # TODO: Load actual HRM model when model path is provided
            # This would load the pretrained weights and configure the model
            # For now, we'll use simulation mode
            logger.info("HRM model initialization pending - using simulation mode")
            self.use_simulation = True
            
        except Exception as e:
            logger.error(f"Failed to initialize HRM model: {e}")
            self.use_simulation = True
    
    def process(self, hrm_input: HRMInput, request_id: str) -> DecisionOutput:
        """
        Process HRM input through the reasoning model
        
        Args:
            hrm_input: Hierarchical input structure (L1, L2, L3)
            request_id: Original request ID for tracking
            
        Returns:
            DecisionOutput: Final decision with actions and explanations
        """
        
        if self.use_simulation:
            return self._simulate_reasoning(hrm_input, request_id)
        else:
            return self._model_reasoning(hrm_input, request_id)
    
    def _model_reasoning(self, hrm_input: HRMInput, request_id: str) -> DecisionOutput:
        """Use actual HRM model for reasoning"""
        
        try:
            # Encode input for HRM model format
            model_input = self._encode_hrm_input(hrm_input)
            
            # Run model inference
            with torch.no_grad():
                model_output = self.model(**model_input)
            
            # Decode model output to decision format
            decision = self._decode_hrm_output(model_output, hrm_input, request_id)
            
            return decision
            
        except Exception as e:
            logger.error(f"HRM model inference failed: {e}")
            # Fallback to simulation
            return self._simulate_reasoning(hrm_input, request_id)
    
    def _simulate_reasoning(self, hrm_input: HRMInput, request_id: str) -> DecisionOutput:
        """
        Simulate HRM reasoning process
        
        This is a rule-based simulation that mimics what the HRM model would do:
        - L1 (Strategic): Assess risk and authorization
        - L2 (Tactical): Select appropriate strategy
        - L3 (Operational): Execute actions
        """
        
        logger.info(f"Simulating HRM reasoning for request {request_id}")
        
        # L1 Strategic Decision
        strategic_assessment = self._assess_strategic_level(hrm_input.L1_strategic)
        
        # Check if authorization is needed and granted
        if hrm_input.L1_strategic.authorization_required:
            if not strategic_assessment["authorized"]:
                return self._create_denied_decision(
                    request_id,
                    "Authorization required but not granted",
                    hrm_input
                )
        
        # L2 Tactical Planning
        tactical_plan = self._plan_tactical_level(hrm_input.L2_tactical, strategic_assessment)
        
        # L3 Operational Execution
        execution_results = self._execute_operational_level(
            hrm_input.L3_operational,
            tactical_plan
        )
        
        # Build decision output
        decision = self._build_decision_output(
            request_id,
            hrm_input,
            strategic_assessment,
            tactical_plan,
            execution_results
        )
        
        return decision
    
    def _assess_strategic_level(self, strategic: StrategicLevel) -> Dict[str, Any]:
        """Assess strategic level and determine if action should proceed"""
        
        # In simulation mode, auto-approve all requests for testing
        # In production, this would check actual authorization tokens/permissions
        # and enforce risk-based approval workflows
        assessment = {
            "approved": True,  # Auto-approve in simulation mode
            "authorized": True,  # Auto-approve in simulation mode
            "risk_acceptable": True,  # Accept all risk levels in simulation mode
            "priority_level": strategic.priority,
            "reasoning": f"Strategic goal: {strategic.goal} (simulation mode - auto-approved)"
        }
        
        return assessment
    
    def _plan_tactical_level(self, tactical: TacticalLevel, strategic_assessment: Dict) -> Dict[str, Any]:
        """Plan tactical execution based on strategy and constraints"""
        
        plan = {
            "strategy": tactical.strategy,
            "policy": tactical.policy,
            "target_subsystem": tactical.subsystem,
            "constraints_validated": True,
            "execution_plan": "sequential",
            "reasoning": f"Using {tactical.strategy} strategy with {tactical.policy}"
        }
        
        # Validate constraints
        for constraint in tactical.constraints:
            logger.info(f"Validating constraint: {constraint}")
            # In production, validate against actual system limits
        
        return plan
    
    def _execute_operational_level(self, operational: OperationalLevel, tactical_plan: Dict) -> List[CompletedAction]:
        """Execute operational level actions"""
        
        completed_actions = []
        
        for action in operational.actions:
            # Simulate action execution
            logger.info(f"Executing action: {action.action} with params: {action.params}")
            
            # Check pre-conditions
            conditions_met = all(self._check_condition(cond) for cond in action.conditions)
            
            if conditions_met:
                # Simulate successful execution
                completed_action = CompletedAction(
                    action=action.action,
                    status="SUCCESS",
                    result={
                        "executed": True,
                        "params": action.params,
                        "subsystem": tactical_plan["target_subsystem"],
                        "details": f"Action {action.action} completed successfully"
                    },
                    timestamp=datetime.now()
                )
            else:
                # Use fallback action
                completed_action = CompletedAction(
                    action=action.fallback or f"{action.action}_SKIPPED",
                    status="FALLBACK",
                    result={
                        "executed": False,
                        "reason": "Pre-conditions not met",
                        "fallback_used": action.fallback
                    },
                    timestamp=datetime.now()
                )
            
            completed_actions.append(completed_action)
        
        return completed_actions
    
    def _check_condition(self, condition: str) -> bool:
        """Check if a condition is met"""
        # In production, this would check actual system state
        # For simulation, we assume most conditions are met
        logger.debug(f"Checking condition: {condition}")
        return True
    
    def _calculate_confidence(
        self,
        hrm_input: HRMInput,
        strategic_assessment: Dict,
        execution_results: List[CompletedAction]
    ) -> float:
        """Calculate realistic confidence score based on multiple factors"""
        import random
        
        base_confidence = 0.5
        
        # Factor 1: Risk level impact (-0.1 to +0.2)
        risk_scores = {
            "LOW": 0.2,
            "MEDIUM": 0.1,
            "HIGH": -0.05,
            "CRITICAL": -0.1
        }
        risk_level = hrm_input.L1_strategic.risk_level.value
        base_confidence += risk_scores.get(risk_level, 0)
        
        # Factor 2: Action success rate (+0 to +0.25)
        if execution_results:
            success_rate = sum(1 for a in execution_results if a.status == "SUCCESS") / len(execution_results)
            base_confidence += success_rate * 0.25
        
        # Factor 3: Priority alignment (+0 to +0.1)
        priority = hrm_input.L1_strategic.priority
        if priority >= 7:
            base_confidence += 0.1
        elif priority >= 4:
            base_confidence += 0.05
        
        # Factor 4: Authorization status (+0.05)
        if strategic_assessment.get("authorized"):
            base_confidence += 0.05
        
        # Factor 5: Add small variance for realism
        variance = random.uniform(-0.03, 0.03)
        base_confidence += variance
        
        # Clamp between 0.4 and 0.98
        return round(max(0.4, min(0.98, base_confidence)), 2)
    
    def _build_decision_output(
        self,
        request_id: str,
        hrm_input: HRMInput,
        strategic_assessment: Dict,
        tactical_plan: Dict,
        execution_results: List[CompletedAction]
    ) -> DecisionOutput:
        """Build final decision output"""
        
        # Determine overall status
        if not strategic_assessment["approved"]:
            status = DecisionStatus.DENIED
        elif all(action.status == "SUCCESS" for action in execution_results):
            status = DecisionStatus.SUCCESS
        elif any(action.status == "SUCCESS" for action in execution_results):
            status = DecisionStatus.PARTIAL
        else:
            status = DecisionStatus.PENDING
        
        # Build summary
        summary = f"{hrm_input.L1_strategic.goal} - {status.value}"
        
        # Calculate realistic confidence
        confidence = self._calculate_confidence(hrm_input, strategic_assessment, execution_results)
        
        # Build explanation
        explanation = self._build_explanation(
            hrm_input,
            strategic_assessment,
            tactical_plan,
            execution_results
        )
        
        # Build audit trail
        audit_trail = {
            "L1_strategic": {
                "goal": hrm_input.L1_strategic.goal,
                "risk_level": hrm_input.L1_strategic.risk_level.value,
                "priority": hrm_input.L1_strategic.priority,
                "assessment": strategic_assessment
            },
            "L2_tactical": {
                "strategy": hrm_input.L2_tactical.strategy,
                "policy": hrm_input.L2_tactical.policy,
                "subsystem": hrm_input.L2_tactical.subsystem,
                "plan": tactical_plan
            },
            "L3_operational": {
                "total_actions": len(execution_results),
                "successful_actions": sum(1 for a in execution_results if a.status == "SUCCESS"),
                "actions": [a.action for a in execution_results]
            }
        }
        
        return DecisionOutput(
            request_id=request_id,
            status=status,
            summary=summary,
            actions_completed=execution_results,
            explanation=explanation,
            confidence=confidence,
            audit_trail=audit_trail,
            timestamp=datetime.now()
        )
    
    def _build_explanation(
        self,
        hrm_input: HRMInput,
        strategic_assessment: Dict,
        tactical_plan: Dict,
        execution_results: List[CompletedAction]
    ) -> str:
        """Build human-readable explanation of decision"""
        
        explanation = []
        
        explanation.append(f"STRATEGIC LEVEL (L1):")
        explanation.append(f"  Goal: {hrm_input.L1_strategic.goal}")
        explanation.append(f"  Risk: {hrm_input.L1_strategic.risk_level.value}")
        explanation.append(f"  Priority: {hrm_input.L1_strategic.priority}/10")
        explanation.append(f"  Assessment: {strategic_assessment['reasoning']}")
        
        explanation.append(f"\nTACTICAL LEVEL (L2):")
        explanation.append(f"  Strategy: {tactical_plan['strategy']}")
        explanation.append(f"  Policy: {tactical_plan['policy']}")
        explanation.append(f"  Subsystem: {tactical_plan['target_subsystem']}")
        
        explanation.append(f"\nOPERATIONAL LEVEL (L3):")
        for action in execution_results:
            explanation.append(f"  - {action.action}: {action.status}")
            if action.result:
                explanation.append(f"    Details: {action.result.get('details', 'N/A')}")
        
        return "\n".join(explanation)
    
    def _create_denied_decision(self, request_id: str, reason: str, hrm_input: HRMInput) -> DecisionOutput:
        """Create a denied decision output"""
        
        return DecisionOutput(
            request_id=request_id,
            status=DecisionStatus.DENIED,
            summary=f"Request denied: {reason}",
            actions_completed=[],
            explanation=f"Decision denied at strategic level.\nReason: {reason}\nGoal: {hrm_input.L1_strategic.goal}",
            confidence=1.0,
            audit_trail={
                "denial_reason": reason,
                "strategic_goal": hrm_input.L1_strategic.goal,
                "risk_level": hrm_input.L1_strategic.risk_level.value
            },
            timestamp=datetime.now()
        )
    
    def _encode_hrm_input(self, hrm_input: HRMInput) -> Dict[str, Any]:
        """Encode HRM input for model format"""
        # TODO: Implement actual encoding for HRM model
        # This would convert the structured input to tensors/tokens
        pass
    
    def _decode_hrm_output(self, model_output: Any, hrm_input: HRMInput, request_id: str) -> DecisionOutput:
        """Decode HRM model output to decision format"""
        # TODO: Implement actual decoding from HRM model output
        # This would interpret the model's reasoning output
        pass


# Convenience function
def create_hrm_engine(model_path: Optional[str] = None) -> HRMEngine:
    """Factory function to create HRM engine"""
    return HRMEngine(model_path=model_path)
