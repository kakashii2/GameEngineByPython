import pygame
import numpy as np

# Pygame 초기화
pygame.init()

# 화면 설정
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Rotating Snowflake with Collision")
clock = pygame.time.Clock()

# 색상
WHITE = (255, 255, 255)
BLUE = (0, 0, 255)
ORANGE = (255, 165, 0)
GRAY = (128, 128, 128)

# Snowflake Shape 생성 함수
def create_detailed_snowflake(center, branch_length, small_branch_length, num_branches=6):
    vertices = []
    angle_step = 2 * np.pi / num_branches

    for i in range(num_branches):
        # 주 가지 생성
        angle = i * angle_step
        main_x = center[0] + branch_length * np.cos(angle)
        main_y = center[1] + branch_length * np.sin(angle)
        vertices.append((main_x, main_y))

        # 세부 가지 생성 (주 가지의 중간 부분)
        mid_x = center[0] + (branch_length / 2) * np.cos(angle)
        mid_y = center[1] + (branch_length / 2) * np.sin(angle)

        small_angle1 = angle + np.pi / 6  # 오른쪽 가지
        small_angle2 = angle - np.pi / 6  # 왼쪽 가지

        small_x1 = mid_x + small_branch_length * np.cos(small_angle1)
        small_y1 = mid_y + small_branch_length * np.sin(small_angle1)

        small_x2 = mid_x + small_branch_length * np.cos(small_angle2)
        small_y2 = mid_y + small_branch_length * np.sin(small_angle2)

        vertices.append((small_x1, small_y1))
        vertices.append((small_x2, small_y2))

    return np.array(vertices)

# Concave 도형을 Convex 파츠로 분해
def decompose_concave(vertices):
    center = np.mean(vertices, axis=0)
    parts = []
    for i in range(len(vertices)):
        next_index = (i + 1) % len(vertices)
        triangle = np.array([center, vertices[i], vertices[next_index]])
        parts.append(triangle)
    return parts

# SAT 충돌 감지 함수
def sat_collision(body1_vertices, body2_vertices):
    axes = get_axes(body1_vertices) + get_axes(body2_vertices)
    for axis in axes:
        projection1 = project(body1_vertices, axis)
        projection2 = project(body2_vertices, axis)
        if not overlap(projection1, projection2):
            return False
    return True

def get_axes(vertices):
    edges = [vertices[i] - vertices[i - 1] for i in range(len(vertices))]
    axes = [np.array([-edge[1], edge[0]]) for edge in edges]
    return [axis / np.linalg.norm(axis) for axis in axes]

def project(vertices, axis):
    projections = [np.dot(vertex, axis) for vertex in vertices]
    return [min(projections), max(projections)]

def overlap(projection1, projection2):
    return not (projection1[1] < projection2[0] or projection2[1] < projection1[0])

# Circle Rigid Body 클래스
class CircleRigidBody:
    def __init__(self, position, radius, color):
        self.position = np.array(position, dtype=float)
        self.radius = radius
        self.color = color

    def update_position(self, position):
        self.position = np.array(position, dtype=float)

    def draw(self):
        pygame.draw.circle(screen, self.color, self.position.astype(int), self.radius)

    def get_vertices(self, num_points=30):
        vertices = []
        for i in range(num_points):
            angle = 2 * np.pi * i / num_points
            x = self.position[0] + self.radius * np.cos(angle)
            y = self.position[1] + self.radius * np.sin(angle)
            vertices.append((x, y))
        return np.array(vertices)

# 고정된 눈 결정 Rigid Body 클래스
class RotatingSnowflake:
    def __init__(self, center, vertices, color):
        self.center = np.array(center, dtype=float)
        self.vertices = vertices
        self.color = color
        self.angle = 0  # 초기 회전 각도 (라디안)

    def rotate(self, rotation_speed, dt):
        """
        눈 결정을 일정 속도로 회전.
        Args:
            rotation_speed (float): 회전 속도 (라디안/초).
            dt (float): 시간 간격.
        """
        self.angle += rotation_speed * dt
        rotation_matrix = np.array([
            [np.cos(self.angle), -np.sin(self.angle)],
            [np.sin(self.angle), np.cos(self.angle)]
        ])
        self.vertices = ((self.vertices - self.center) @ rotation_matrix.T) + self.center

    def draw(self):
        pygame.draw.polygon(screen, self.color, self.vertices.astype(int))

# 충돌 감지 함수
def concave_collision(concave_parts, circle_vertices):
    for part in concave_parts:
        if sat_collision(part, circle_vertices):
            return True
    return False

# 초기화
snowflake_vertices = create_detailed_snowflake(center=(WIDTH // 2, HEIGHT // 2), branch_length=100, small_branch_length=30)
rotating_snowflake = RotatingSnowflake(center=(WIDTH // 2, HEIGHT // 2), vertices=snowflake_vertices, color=BLUE)
concave_parts = decompose_concave(snowflake_vertices)

circle_body = CircleRigidBody(position=(200, 200), radius=15, color=GRAY)

# 메인 루프
running = True
dt = 1 / 60  # 고정 시간 간격
rotation_speed = np.pi / 18  # 초당 10도 (라디안/초)

while running:
    screen.fill(WHITE)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # 눈 결정 회전
    rotating_snowflake.rotate(rotation_speed, dt)

    # 마우스 위치 따라다니기
    mouse_position = pygame.mouse.get_pos()
    circle_body.update_position(mouse_position)

    # 충돌 감지
    circle_vertices = circle_body.get_vertices(30)
    concave_parts = decompose_concave(rotating_snowflake.vertices)
    if concave_collision(concave_parts, circle_vertices):
        rotating_snowflake.color = ORANGE
    else:
        rotating_snowflake.color = BLUE

    # 렌더링
    rotating_snowflake.draw()
    circle_body.draw()

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
