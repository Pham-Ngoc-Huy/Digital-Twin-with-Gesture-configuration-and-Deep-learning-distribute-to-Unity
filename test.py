from src.kinematics import LocalFrameBuilder
x = [1, 0, 0]
y = [0, 1, 0]
builder = LocalFrameBuilder(x, y)
R = builder.process()
print("R matrix: ", R)