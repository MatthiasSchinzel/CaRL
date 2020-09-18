import numpy as np
import pygame
import cv2
import pathlib

class State:
    """
    vehicle state class
    """
    def __init__(self, x=0.0, y=0.0, yaw=0.0, v=0.0):
        self.x = x
        self.y = y
        self.yaw = yaw
        self.v = v
        self.predelta = None


class carl:
    def __init__(self):
        self.Target_FPS = 30
        # iterative paramter
        self.MAX_ITER = 3  # Max iteration
        self.DU_TH = 0.1  # iteration finish param

        self.TARGET_SPEED = 50.0 / 3.6  # [m/s] target speed
        self.N_IND_SEARCH = 10  # Search index number
        self.a1 = 10  # cw deceleration
        # DT = 0.02  # [s] time tick
        self.DT = 1/self.Target_FPS
        # Vehicle parameters
        self.LENGTH = 4.5 * 10  # [m]
        self.WIDTH = 2.0 * 10  # [m]
        self.BACKTOWHEEL = 1.0 * 10  # [m]
        self.WHEEL_LEN = .3 * 10  # [m]
        self.WHEEL_WIDTH = .2 * 10  # [m]
        self.TREAD = .7 * 10  # [m]
        self.WB = 2.5 * 10  # [m]

        self.Simultation_speed = 1
        self.MAX_STEER = np.deg2rad(10.0)  # maximum steering angle [rad]
        self.MAX_DSTEER = np.deg2rad(2.0)  # maximum steering speed [rad/s]
        self.MAX_SPEED = 500 * self.Simultation_speed / 3.6  # max speed[m/s]
        self.MIN_SPEED = -200 * self.Simultation_speed / 3.6  # min speed[m/s]
        self.MAX_ACCEL = 100 * self.Simultation_speed  # maximum accel [m/ss]

        self.show_animation = True
        # Front view parameters
        self.dist = 200
        self.viewing_angle = 45  # 60
        self.front_center_offset = self.WIDTH*(3/4)  # *2

        self.index = 0
        self.score = 0
        k = 0
        if k == 0:
            self.impath = str(pathlib.Path(__file__).parent.absolute()) + "/Tracks/BigMap.png"
        if k == 1:
            self.impath = str(pathlib.Path(__file__).parent.absolute()) + "/Tracks/TestTrack.png"
        if k == 2:
            self.impath = str(pathlib.Path(__file__).parent.absolute()) + "/Tracks/Map3.png"
        if k == 3:
            self.impath = str(pathlib.Path(__file__).parent.absolute()) + "/Tracks/MapWithTrinagleAndSquare.png"
        # load map
        self.img = cv2.imread(self.impath)
        # get start and end point
        self.indices = np.where(
            np.all(np.asarray(self.img) == (0, 255, 0), axis=-1))
        self.indexes = zip(self.indices[0], self.indices[1])
        pygame.init()
        self.clock = pygame.time.Clock()
        self.background = pygame.image.load(self.impath)
        # target_size = background.get_rect().size
        self.flag_plot_frontview = True
        if self.flag_plot_frontview is True:
            self.target_size = (int(1280), int(704))
        else:
            self.target_size = self.background.get_rect().size
        self.flag_showBackend = False
        self.screen_orignal = 0
        self.Target_FPS = 0
        self.screen = pygame.Surface(self.background.get_rect().size)
        self.trail = pygame.Surface(self.background.get_rect().size)
        self.state = State(
            x=self.indices[1][0], y=self.indices[0][0], yaw=0, v=0.0)
        self.ai, self.di = 0, 0
        self.r_old = 0
        self.done = False
        self.yaw_old = self.di
        self.outline = []
        self.front_view = []
        self.current_reward = 0
        self.ai_old = 0
        self.time_penelization = 0.2
        self.past_actions = np.zeros([2, 2])  # np.zeros([10,2])
        self.selfdriving = False
        self.flag_check_underground = True
        self.map_id = 0
        self.flag_last_round = 0

    def reset(self):
        self.__init__()

    def load_next_map(self):
        if self.map_id == 1:
            self.impath = str(pathlib.Path(__file__).parent.absolute()) + "/Tracks/TestTrack.png"
        if self.map_id == 2:
            self.impath = str(pathlib.Path(__file__).parent.absolute()) + "/Tracks/Map3.png"
        if self.map_id == 3:
            self.impath = str(pathlib.Path(__file__).parent.absolute()) + "/Tracks/MapWithTrinagleAndSquare.png"
            self.flag_last_round = 1
        self.img = cv2.imread(self.impath)
        self.indices = np.where(
            np.all(np.asarray(self.img) == (0, 255, 0), axis=-1))
        self.indexes = zip(self.indices[0], self.indices[1])
        self.background = pygame.image.load(self.impath)
        # target_size = background.get_rect().size
        if self.flag_plot_frontview is True:
            self.target_size = (int(1280/4), int(704/4))
        else:
            self.target_size = self.background.get_rect().size
        self.screen = pygame.Surface(self.background.get_rect().size)
        self.trail = pygame.Surface(self.background.get_rect().size)
        # self.state = State(x=self.indices[0][0]+ \
        # self.LENGTH/2,y=self.indices[1][0]-self.WIDTH/2, yaw=0, v=0.0)
        self.state = State(
                    x=self.indices[1][0], y=self.indices[0][0], yaw=0, v=0.0)
        self.ai, self.di = 0, 0
        self.r_old = 0
        self.yaw_old = self.di
        self.outline = []
        self.front_view = []
        self.ai_old = 0
        self.past_actions = np.zeros([2, 2])  # np.zeros([10,2])
        self.step(np.array([0, 0]))

    def get_frontview(self):
        Rot1 = np.array([[np.cos(self.state.yaw), np.sin(self.state.yaw)],
                        [-np.sin(self.state.yaw), np.cos(self.state.yaw)]])
        front_center_right = np.array(
                        [[(self.LENGTH - self.BACKTOWHEEL)],
                         [self.front_center_offset]]).T.dot(Rot1).T
        front_center_left = np.array(
                        [[(self.LENGTH - self.BACKTOWHEEL)],
                         [-self.front_center_offset]]).T.dot(Rot1).T
        front_center_right[0, :] += self.state.x
        front_center_right[1, :] += self.state.y
        front_center_left[0, :] += self.state.x
        front_center_left[1, :] += self.state.y
        right_dist_point = np.array(
                [[(self.LENGTH - self.BACKTOWHEEL)+self.dist],
                 [np.tan(np.deg2rad(self.viewing_angle))*self.dist]]
                 ).T.dot(Rot1).T
        left_dist_point = np.array(
                [[(self.LENGTH - self.BACKTOWHEEL)+self.dist],
                 [np.tan(np.deg2rad(-self.viewing_angle))*self.dist]]
                 ).T.dot(Rot1).T
        right_dist_point[0, :] += self.state.x
        right_dist_point[1, :] += self.state.y
        left_dist_point[0, :] += self.state.x
        left_dist_point[1, :] += self.state.y
        debug = False
        if debug is True:
            try:
                pygame.draw.circle(self.screen, [0, 255, 0], tuple(
                    front_center_right.astype('uint32').reshape(1, -1)[0]), 3)
            except Exception:
                pass
            try:
                pygame.draw.circle(self.screen, [0, 255, 0], tuple(
                    front_center_left.astype('uint32').reshape(1, -1)[0]), 3)
            except Exception:
                pass
            try:
                pygame.draw.circle(self.screen, [0, 255, 0], tuple(
                    right_dist_point.astype('uint32').reshape(1, -1)[0]), 3)
            except Exception:
                pass
            try:
                pygame.draw.circle(self.screen, [0, 255, 0], tuple(
                    left_dist_point.astype('uint32').reshape(1, -1)[0]), 3)
            except Exception:
                pass
        dst_h = int(self.target_size[1]/2)  # - self.ai*0.1)
        dst_w = self.target_size[0]
        src = np.float32(
            [[left_dist_point[0, :], left_dist_point[1, :]],
             [right_dist_point[0, :], right_dist_point[1, :]],
             [front_center_left[0, :], front_center_left[1, :]],
             [front_center_right[0, :], front_center_right[1, :]]])
        dst = np.float32([[0, 0], [0, dst_w], [dst_h, 0], [dst_h, dst_w]])
        M = cv2.getPerspectiveTransform(src, dst)  # The transformation matrix
        warped_img = cv2.warpPerspective(
            self.img, M, (dst_h, dst_w), borderMode=cv2.BORDER_CONSTANT,
            borderValue=(255, 255, 255))  # Image warping
        lower = (0, 0, 1)  # lower bound for each channel
        upper = (0, 0, 255)  # upper bound for each channel
        # create the mask and use it to change the colors
        mask = cv2.inRange(warped_img, lower, upper)
        warped_img[mask > 0] = [0, 0, 0]
        w = np.full((self.target_size[0], self.target_size[1], 3), 255)
        w[:, int(self.target_size[1]-dst_h)::, :] = cv2.cvtColor(
            warped_img, cv2.COLOR_BGR2RGB)
        self.front_view = cv2.cvtColor(w.astype("uint8"), cv2.COLOR_RGB2GRAY)
        flag_write_output = False
        if flag_write_output is True:
            cv2.imwrite(
                "PygameCarGame/" + str(self.index) + ".png", self.front_view.T)
            self.index = self.index + 1
        return w

    def check_underground(self):
        src = np.float32(
            [[self.outline[0, 0], self.outline[1, 0]], [self.outline[0, 1],
             self.outline[1, 1]], [self.outline[0, 2], self.outline[1, 2]],
             [self.outline[0, 3], self.outline[1, 3]]])
        dst = np.float32(
            [[0, 0], [0, self.LENGTH], [self.WIDTH, self.LENGTH],
             [self.WIDTH, 0]])
        M = cv2.getPerspectiveTransform(src, dst)  # The transformation matrix
        warped_img = cv2.warpPerspective(
            self.img, M, (int(self.WIDTH), int(self.LENGTH)),
            borderMode=cv2.BORDER_CONSTANT,
            borderValue=(255, 255, 255))  # Image warping
        if np.any(np.all(warped_img == np.array([0, 0, 255]), axis=-1)):
            if self.flag_last_round == 1:
                self.done = True
            # self.score = self.score + 100
            print("Finishline!!")
            self.map_id += 1
            self.load_next_map()
            # self.done = True
        if self.flag_check_underground is True:
            if np.any(np.all(warped_img ==
               np.array([255, 255, 255]), axis=-1)):
                self.done = True
        return np.min(np.asarray(warped_img)), warped_img

    def plot_car(self):
        self.outline = np.array(
            [[-self.BACKTOWHEEL, (self.LENGTH - self.BACKTOWHEEL),
             (self.LENGTH - self.BACKTOWHEEL),
             -self.BACKTOWHEEL, -self.BACKTOWHEEL],
             [self.WIDTH / 2, self.WIDTH / 2,
              - self.WIDTH / 2, -self.WIDTH / 2,
              self.WIDTH / 2]])

        fr_wheel = np.array(
            [[self.WHEEL_LEN, -self.WHEEL_LEN,
             -self.WHEEL_LEN, self.WHEEL_LEN, self.WHEEL_LEN],
             [-self.WHEEL_WIDTH - self.TREAD,
              -self.WHEEL_WIDTH - self.TREAD, self.WHEEL_WIDTH - self.TREAD,
              self.WHEEL_WIDTH - self.TREAD, -self.WHEEL_WIDTH - self.TREAD]])

        rr_wheel = np.copy(fr_wheel)
        fl_wheel = np.copy(fr_wheel)
        fl_wheel[1, :] *= -1
        rl_wheel = np.copy(rr_wheel)
        rl_wheel[1, :] *= -1

        Rot1 = np.array([[np.cos(self.state.yaw), np.sin(self.state.yaw)],
                         [-np.sin(self.state.yaw), np.cos(self.state.yaw)]])
        Rot2 = np.array([[np.cos(self.di), np.sin(self.di)],
                         [-np.sin(self.di), np.cos(self.di)]])

        fr_wheel = (fr_wheel.T.dot(Rot2)).T
        fl_wheel = (fl_wheel.T.dot(Rot2)).T
        fr_wheel[0, :] += self.WB
        fl_wheel[0, :] += self.WB

        fr_wheel = (fr_wheel.T.dot(Rot1)).T
        fl_wheel = (fl_wheel.T.dot(Rot1)).T

        self.outline = (self.outline.T.dot(Rot1)).T
        rr_wheel = (rr_wheel.T.dot(Rot1)).T
        rl_wheel = (rl_wheel.T.dot(Rot1)).T

        self.outline[0, :] += self.state.x
        self.outline[1, :] += self.state.y
        fr_wheel[0, :] += self.state.x
        fr_wheel[1, :] += self.state.y
        rr_wheel[0, :] += self.state.x
        rr_wheel[1, :] += self.state.y
        fl_wheel[0, :] += self.state.x
        fl_wheel[1, :] += self.state.y
        rl_wheel[0, :] += self.state.x
        rl_wheel[1, :] += self.state.y
        min, warped_img = self.check_underground()
        if min < 128:
            white = [255, 0, 0]
        else:
            white = [0, 255, 0]
        r = pygame.draw.lines(
            self.screen, white, True, tuple(self.outline.T.tolist()))
        pygame.draw.lines(self.screen, white, True, tuple(fr_wheel.T.tolist()))
        pygame.draw.lines(self.screen, white, True, tuple(rr_wheel.T.tolist()))
        pygame.draw.lines(self.screen, white, True, tuple(fl_wheel.T.tolist()))
        pygame.draw.lines(self.screen, white, True, tuple(rl_wheel.T.tolist()))
        subrect = 0

        # panalize shakiness
        self.current_reward = 0
        self.current_reward -= 10*np.power(
            (np.abs(self.yaw_old - self.state.yaw)/self.MAX_STEER), 0.4)
        self.current_reward -= np.abs(self.ai_old - self.ai)/self.MAX_ACCEL
        self.current_reward -= self.time_penelization
        if self.r_old != 0:
            self.trail.fill([0, 0, 0], self.r_old)
            subrect = self.trail.subsurface(r.union(self.r_old))
            s = subrect.get_size()
            x = 0
            if (not(r.x == self.r_old.x and r.y == self.r_old.y) and
               not r.contains(self.r_old) and not self.r_old.contains(r)):
                for i in range(0, s[0]):
                    for j in range(0, s[1]):
                        if white == [255, 0, 0]:
                            if (subrect.get_at([i, j]) ==
                               ((255), (0), (0), (255))):
                                x = x + 1
                if x == 0:
                    self.current_reward += 4 + (self.state.v/self.MAX_SPEED)*5
                    self.score = self.score
            self.trail.fill([255, 0, 0], self.r_old)
        if white == [255, 0, 0]:
            self.trail.fill(white, r)
            self.r_old = r
        else:
            self.r_old = 0
        self.yaw_old = self.state.yaw
        self.ai_old = self.ai

    def update_state(self):
        # input check
        if self.di >= self.MAX_STEER:
            self.di = self.MAX_STEER
        elif self.di <= -self.MAX_STEER:
            self.di = -self.MAX_STEER
        self.state.x = self.state.x + \
            self.state.v * np.cos(self.state.yaw) * self.DT
        self.state.y = self.state.y + \
            self.state.v * np.sin(self.state.yaw) * self.DT
        self.state.yaw = self.state.yaw + \
            self.state.v / self.WB * np.tan(self.di) * self.DT
        self.state.v = self.state.v + self.ai * self.DT
        if self.state.v > 0:
            self.state.v = self.state.v - self.a1 * self.DT
        if self.state.v < 0:
            self.state.v = self.state.v + self.a1 * self.DT
        if self.state. v > self.MAX_SPEED:
            self.state.v = self.MAX_SPEED
        elif self.state. v < self.MIN_SPEED:
            self.state.v = self.MIN_SPEED

    def play_game_manually(self):
        self.flag_showBackend = True
        self.flag_check_underground = False
        self.screen_orignal = pygame.display.set_mode(self.target_size)
        self.Target_FPS = 30
        flag_average = 0
        while not self.done:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.done = True
            ai, di = 0, 0
            status = pygame.key.get_pressed()
            if status[pygame.K_a]:
                di = -1
            if status[pygame.K_d]:
                di = 1
            if status[pygame.K_w]:
                ai = 1
            if status[pygame.K_s]:
                ai = -1
            if status[pygame.K_q]:
                self.done = True

            action = np.array([ai, di])
            if flag_average == 1:
                self.step((action + self.past_actions[0, :])/2)
            else:
                self.step(action)
            pygame.display.flip()
            _ = self.clock.tick_busy_loop(self.Target_FPS)
            print(self.current_reward)
            self.score += self.current_reward
        return self.score

    def step(self, action):
        ai = action[0] * self.MAX_ACCEL
        di = action[1] * self.MAX_STEER
        self.ai = ai
        self.di = di
        self.update_state()
        if self.flag_plot_frontview is False:
            self.screen.blit(self.background, (0, 0))
        self.plot_car()
        if self.flag_plot_frontview is False:
            if self.flag_showBackend is True:
                self.screen_orignal.blit(self.screen, (0, 0))
        else:
            w = self.get_frontview()
            w = pygame.surfarray.make_surface(w)
            if self.flag_showBackend is True:
                self.screen_orignal.blit(w, (0, 0))
        self.past_actions = np.roll(self.past_actions, 1)
        self.past_actions[0, 0] = action[0]
        self.past_actions[0, 1] = action[1]
        return self.front_view, self.current_reward, self.done, 0

    def render(self):
        return self.front_view

    class action_space:
        low = np.array([-1, -1])
        high = np.array([1, 1])

        def sample():
            return np.random.uniform(low=-1, high=1.0, size=2)
