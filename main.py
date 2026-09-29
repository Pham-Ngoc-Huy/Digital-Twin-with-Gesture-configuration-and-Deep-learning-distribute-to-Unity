import numpy as np

from kinematics import vector_between, angle_between


# -------------------------
# Simulated MediaPipe data
# -------------------------

MCP = np.array([0.0, 0.0, 0.0])
PIP = np.array([1.0, 0.0, 0.0])
DIP = np.array([1.8, 0.5, 0.0])


# -------------------------
# Calculate bone vectors
# -------------------------

v_mcp_pip = vector_between(MCP, PIP)
v_pip_dip = vector_between(PIP, DIP)


print("MCP -> PIP:", v_mcp_pip)
print("PIP -> DIP:", v_pip_dip)


# -------------------------
# Calculate joint angle
# -------------------------

angle = angle_between(v_mcp_pip, v_pip_dip)

print("Joint angle:", angle, "degrees")