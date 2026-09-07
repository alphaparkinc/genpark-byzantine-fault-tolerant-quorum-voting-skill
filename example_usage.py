"""
Demonstration of Byzantine Fault Tolerant Quorum Voting Skill
"""

from client import PBFTCluster

def main():
    print("=== Testing PBFT Consensus with 4 Nodes (N=4, f=1 Byzantine) ===")
    cluster = PBFTCluster(node_count=4, byzantine_count=1)
    
    task_payload = {"action": "EXECUTE_TOOL", "tool": "database_write", "record_id": "txn_8849"}
    print(f"Proposing payload: {task_payload}")
    
    result = cluster.execute_consensus(task_payload)
    print("Consensus Result:", result)
    assert result["consensus_achieved"] is True
    print(f"SUCCESS: Quorum satisfied despite {result['byzantine_nodes']} Byzantine node!")

    print("\n=== Testing PBFT Consensus with 7 Nodes (N=7, f=2 Byzantine) ===")
    cluster_7 = PBFTCluster(node_count=7, byzantine_count=2)
    result_7 = cluster_7.execute_consensus({"system_update": "v2.5_deploy"})
    print("Consensus Result 7-node:", result_7)
    assert result_7["consensus_achieved"] is True
    print("PBFT Quorum Voting Verification PASS!")

if __name__ == "__main__":
    main()
