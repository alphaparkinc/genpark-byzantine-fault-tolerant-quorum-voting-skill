"""
MCP Server for Byzantine Fault Tolerant Quorum Voting Skill
"""

import json
import sys
from client import PBFTCluster

def handle_call(name: str, args: dict) -> dict:
    if name == "validate_quorum":
        nodes = args.get("nodes", 4)
        byz = args.get("byzantine_faults", 1)
        payload = args.get("payload", {"test": True})
        try:
            cluster = PBFTCluster(node_count=nodes, byzantine_count=byz)
            return cluster.execute_consensus(payload)
        except Exception as e:
            return {"error": str(e)}
    return {"error": f"Unknown tool: {name}"}

def main():
    for line in sys.stdin:
        if not line.strip():
            continue
        req = json.loads(line)
        res = handle_call(req.get("method"), req.get("params", {}))
        sys.stdout.write(json.dumps(res) + "\n")
        sys.stdout.flush()

if __name__ == "__main__":
    main()
