import sys
import os

# ── Add ml/ folder to path (same as backend) ──
sys.path.append(os.path.join(os.path.dirname(__file__), "../ml"))
from knowledge_graph import get_role_requirements, get_all_roles

roles = get_all_roles()

# Check 1: Coverage — all roles have skills
covered = 0
for role in roles:
    skills = get_role_requirements(role)
    if len(skills) >= 5:
        covered += 1
    print(f"{role:35} → {len(skills)} skills")

print(f"\nCoverage: {covered}/{len(roles)} roles have 5+ skills")
print(f"Coverage Rate: {covered/len(roles)*100:.1f}%")

# Check 2: Manual validation of top 5 skills per key role
key_roles = ["Data Scientist", "Software Engineer", "DevOps Engineer"]
for role in key_roles:
    skills = get_role_requirements(role)
    print(f"\nTop 5 skills for {role}:")
    for s in skills[:5]:
        print(f"  - {s}")