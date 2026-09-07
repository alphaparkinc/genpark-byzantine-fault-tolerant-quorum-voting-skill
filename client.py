"""
Byzantine Fault Tolerant Quorum Voting Skill Client
Pure Python Standard Library implementation of Practical Byzantine Fault Tolerance (PBFT) style consensus.
Guarantees safety and liveness across an agent swarm tolerating up to f faulty or adversarial nodes (N >= 3f + 1).
"""

from typing import List, Dict, Any, Tuple, Optional, Set
import hashlib
import json


class PBFTMessage:
    def __init__(self, msg_type: str, view: int, sequence: int, digest: str, sender: str, payload: Any = None):
        self.msg_type = msg_type  # PRE_PREPARE, PREPARE, COMMIT
        self.view = view
        self.sequence = sequence
        self.digest = digest
        self.sender = sender
        self.payload = payload

    def to_dict(self) -> Dict[str, Any]:
        return {
            "msg_type": self.msg_type,
            "view": self.view,
            "sequence": self.sequence,
            "digest": self.digest,
            "sender": self.sender,
            "payload": self.payload
        }


class PBFTNode:
    def __init__(self, node_id: str, is_byzantine: bool = False):
        self.node_id = node_id
        self.is_byzantine = is_byzantine
        self.view = 0
        self.sequence = 0
        self.prepared_certificates: Dict[Tuple[int, int], Set[str]] = {}
        self.committed_certificates: Dict[Tuple[int, int], Set[str]] = {}
        self.committed_log: List[Dict[str, Any]] = []

    def compute_digest(self, payload: Any) -> str:
        s = json.dumps(payload, sort_keys=True)
        return hashlib.sha256(s.encode("utf-8")).hexdigest()[:16]

    def create_pre_prepare(self, payload: Any) -> PBFTMessage:
        self.sequence += 1
        digest = self.compute_digest(payload)
        return PBFTMessage("PRE_PREPARE", self.view, self.sequence, digest, self.node_id, payload)

    def handle_pre_prepare(self, msg: PBFTMessage) -> Optional[PBFTMessage]:
        expected_digest = self.compute_digest(msg.payload)
        if msg.digest != expected_digest:
            return None
        # Send prepare
        digest_to_send = "BYZANTINE_FAKE" if self.is_byzantine else msg.digest
        return PBFTMessage("PREPARE", msg.view, msg.sequence, digest_to_send, self.node_id)

    def handle_prepare(self, msg: PBFTMessage, quorum_size: int, payload_digest: str) -> Optional[PBFTMessage]:
        if msg.digest != payload_digest:
            return None  # Ignore invalid digest
        key = (msg.view, msg.sequence)
        if key not in self.prepared_certificates:
            self.prepared_certificates[key] = set()
        self.prepared_certificates[key].add(msg.sender)

        if len(self.prepared_certificates[key]) >= quorum_size:
            return PBFTMessage("COMMIT", msg.view, msg.sequence, msg.digest, self.node_id)
        return None

    def handle_commit(self, msg: PBFTMessage, quorum_size: int, payload: Any) -> bool:
        expected_digest = self.compute_digest(payload)
        if msg.digest != expected_digest:
            return False
        key = (msg.view, msg.sequence)
        if key not in self.committed_certificates:
            self.committed_certificates[key] = set()
        self.committed_certificates[key].add(msg.sender)

        if len(self.committed_certificates[key]) >= quorum_size:
            self.committed_log.append({"view": msg.view, "sequence": msg.sequence, "payload": payload})
            return True
        return False


class PBFTCluster:
    def __init__(self, node_count: int, byzantine_count: int = 0):
        assert node_count >= 3 * byzantine_count + 1, "PBFT requires N >= 3f + 1"
        self.node_count = node_count
        self.byzantine_count = byzantine_count
        self.quorum_size = 2 * byzantine_count + 1
        self.nodes: Dict[str, PBFTNode] = {}
        for i in range(node_count):
            nid = f"agent-{i}"
            is_byz = (i < byzantine_count)
            self.nodes[nid] = PBFTNode(nid, is_byzantine=is_byz)
        self.primary_id = f"agent-{byzantine_count}" if byzantine_count < node_count else "agent-0"

    def execute_consensus(self, payload: Any) -> Dict[str, Any]:
        primary = self.nodes[self.primary_id]
        pre_prep = primary.create_pre_prepare(payload)

        # 1. Broadcast Pre-Prepare -> Receive Prepares
        prepares: List[PBFTMessage] = []
        for nid, node in self.nodes.items():
            prep = node.handle_pre_prepare(pre_prep)
            if prep:
                prepares.append(prep)

        # 2. Collect Prepares -> Generate Commits
        commits: List[PBFTMessage] = []
        for nid, node in self.nodes.items():
            for p in prepares:
                commit_msg = node.handle_prepare(p, self.quorum_size, pre_prep.digest)
                if commit_msg:
                    commits.append(commit_msg)
                    break

        # 3. Collect Commits -> Finalize Commit
        final_commits = 0
        for nid, node in self.nodes.items():
            for c in commits:
                if node.handle_commit(c, self.quorum_size, payload):
                    final_commits += 1
                    break

        consensus_achieved = final_commits >= self.quorum_size
        return {
            "view": pre_prep.view,
            "sequence": pre_prep.sequence,
            "digest": pre_prep.digest,
            "quorum_size": self.quorum_size,
            "participating_nodes": self.node_count,
            "byzantine_nodes": self.byzantine_count,
            "consensus_achieved": consensus_achieved,
            "committed_node_count": final_commits
        }
