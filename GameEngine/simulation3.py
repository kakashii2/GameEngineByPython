import pygame
import numpy as np

# Pygame 초기화
pygame.init()

# 화면 설정
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Cloth Simulation with Color")
clock = pygame.time.Clock()

# 색상
WHITE = (255, 255, 255)
GRAY = (200, 200, 200)
BLUE = (70, 130, 180)  # 망토 색상

# 클로스 설정
NUM_X, NUM_Y = 15, 10  # 가로, 세로 질량점 개수
SPACING = 30  # 질량점 간 거리 (픽셀)
GRAVITY = np.array([0, 0.3])  # 중력 벡터
DAMPING = 0.95  # 속도 감쇠
SPRING_STIFFNESS = 0.5  # 스프링 강도

# 질량점 클래스
class Particle:
    def __init__(self, x, y, fixed=False):
        self.position = np.array([x, y], dtype=float)
        self.previous_position = self.position.copy()
        self.fixed = fixed
        self.acceleration = np.zeros(2, dtype=float)

    def apply_force(self, force):
        if not self.fixed:
            self.acceleration += force

    def verlet(self):
        if not self.fixed:
            velocity = (self.position - self.previous_position) * DAMPING
            self.previous_position = self.position.copy()
            self.position += velocity + self.acceleration
            self.acceleration = np.zeros(2, dtype=float)

# 스프링 클래스
class Spring:
    def __init__(self, particle_a, particle_b):
        self.particle_a = particle_a
        self.particle_b = particle_b
        self.rest_length = np.linalg.norm(particle_a.position - particle_b.position)

    def apply_spring_force(self):
        delta = self.particle_b.position - self.particle_a.position
        distance = np.linalg.norm(delta)
        if distance == 0:
            return
        force = SPRING_STIFFNESS * (distance - self.rest_length) * (delta / distance)
        self.particle_a.apply_force(force)
        self.particle_b.apply_force(-force)

# 질량점과 스프링 생성
particles = []
springs = []

# 질량점 배열 생성
for y in range(NUM_Y):
    for x in range(NUM_X):
        fixed = (y == 0)  # 상단 모든 질량점 고정
        particles.append(Particle(x * SPACING + WIDTH // 4, y * SPACING, fixed))

# 스프링 연결
for y in range(NUM_Y):
    for x in range(NUM_X):
        idx = y * NUM_X + x
        if x < NUM_X - 1:  # 오른쪽 연결
            springs.append(Spring(particles[idx], particles[idx + 1]))
        if y < NUM_Y - 1:  # 아래쪽 연결
            springs.append(Spring(particles[idx], particles[idx + NUM_X]))

# 망토 색상 채우기
def render_cloth():
    for y in range(NUM_Y - 1):
        for x in range(NUM_X - 1):
            idx = y * NUM_X + x
            p1, p2, p3 = particles[idx], particles[idx + 1], particles[idx + NUM_X]
            p4 = particles[idx + NUM_X + 1]
            # 삼각형 1
            pygame.draw.polygon(screen, BLUE, [p1.position, p2.position, p3.position])
            # 삼각형 2
            pygame.draw.polygon(screen, BLUE, [p2.position, p4.position, p3.position])

# 렌더링 함수
def render_particles():
    for particle in particles:
        pygame.draw.circle(screen, GRAY, particle.position.astype(int), 2)

# 메인 루프
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            # 마우스 클릭으로 질량점에 힘 추가
            mouse_pos = np.array(pygame.mouse.get_pos())
            for particle in particles:
                if np.linalg.norm(particle.position - mouse_pos) < SPACING:
                    particle.apply_force(np.array([0, -10]))  # 바람 효과

    # 물리 계산
    for spring in springs:
        spring.apply_spring_force()
    for particle in particles:
        particle.apply_force(GRAVITY)
        particle.verlet()

    # 렌더링
    screen.fill(WHITE)
    render_cloth()  # 망토 색상 렌더링
    render_particles()  # 질량점 렌더링
    pygame.display.flip()
    clock.tick(30)  # FPS 제한

pygame.quit()
