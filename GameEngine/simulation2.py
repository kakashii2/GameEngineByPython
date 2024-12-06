import pygame
import numpy as np
import random

# Pygame 초기화
pygame.init()

# 화면 설정
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Realistic Fire Simulation")
clock = pygame.time.Clock()

# 색상
BLACK = (0, 0, 0)

# 불 입자 클래스
class FireParticle:
    def __init__(self, x, y):
        self.position = np.array([x, y], dtype=float)
        self.previous_position = self.position.copy()
        self.acceleration = np.zeros(2, dtype=float)
        self.velocity = np.random.uniform(-1.5, 1.5, 2)  # 초기 속도
        self.size = random.randint(10, 20)  # 입자 크기
        self.lifetime = random.randint(80, 150)  # 수명
        self.color = (255, 200, 100)  # 초기 색상 (밝은 노란색)

    def apply_force(self, force):
        """입자에 힘을 적용"""
        self.acceleration += force

    def verlet_integration(self):
        """Verlet Integration으로 위치 업데이트"""
        velocity = (self.position - self.previous_position) * 0.95  # 감쇠 적용
        self.previous_position = self.position.copy()
        self.position += velocity + self.acceleration
        self.acceleration = np.zeros(2, dtype=float)

    def update(self):
        """수명 감소 및 색상, 크기, 투명도 변화"""
        self.lifetime -= 1
        r, g, b = self.color
        self.color = (max(r - 3, 100), max(g - 5, 0), max(b - 10, 0))  # 점점 어두운 색으로 변화
        self.size = max(self.size - 0.2, 1)  # 크기 감소

    def is_dead(self):
        """입자가 소멸되었는지 확인"""
        return self.lifetime <= 0

    def draw(self):
        """입자를 화면에 그리기"""
        alpha = max(self.lifetime / 150, 0)  # 수명에 따라 투명도 조정
        color_with_alpha = tuple(int(c * alpha) for c in self.color)  # 투명도 반영
        pygame.draw.circle(screen, color_with_alpha, self.position.astype(int), int(self.size))

# 불 시스템 클래스
class FireSystem:
    def __init__(self, x, y, emission_rate):
        self.origin = np.array([x, y], dtype=float)
        self.particles = []
        self.emission_rate = emission_rate

    def emit(self):
        """새로운 입자를 생성"""
        for _ in range(self.emission_rate):
            self.particles.append(FireParticle(self.origin[0], self.origin[1]))

    def update(self):
        """입자 업데이트 및 소멸 처리"""
        for particle in self.particles[:]:
            # 힘 적용: 중력과 난류
            particle.apply_force(np.array([0, -0.2]))  # 중력 (위로 올라가는 힘)
            particle.apply_force(np.random.uniform(-0.3, 0.3, 2))  # 난류 효과
            particle.verlet_integration()
            particle.update()
            if particle.is_dead():
                self.particles.remove(particle)

    def draw(self):
        """모든 입자 그리기"""
        for particle in self.particles:
            particle.draw()

# 불 시스템 초기화
fire_system = FireSystem(WIDTH // 2, HEIGHT - 100, 40)  # 더 큰 불꽃 시뮬레이션

# 메인 루프
running = True
while running:
    screen.fill(BLACK)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # 불 시스템 업데이트 및 그리기
    fire_system.emit()
    fire_system.update()
    fire_system.draw()

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
