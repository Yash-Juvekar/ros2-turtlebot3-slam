import math

import rclpy
from rclpy.node import Node
from geometry_msgs.msg import TwistStamped
from sensor_msgs.msg import LaserScan

SAFE_DISTANCE = 0.5    # closer than this in front = start turning
CLEAR_DISTANCE = 0.8   # must see this much free space before driving again
FORWARD_SPEED = 0.2    # m/s (Burger max is about 0.22 m/s, but we can go a bit faster)
TURN_SPEED = 0.8       # rad/s


class ObstacleAvoider(Node):
    def __init__(self):
        super().__init__('obstacle_avoider')
        self.publisher_ = self.create_publisher(TwistStamped, '/cmd_vel', 10)
        self.subscription = self.create_subscription(
            LaserScan, '/scan', self.scan_callback, 10)
        self.turn_dir = 0.0   # 0 = not turning, +1 = left, -1 = right
        self.get_logger().info('obstacle_avoider started')

    def sector_min(self, msg, start_deg, end_deg):
        """Smallest valid distance between two angles (degrees)."""
        closest = msg.range_max
        for deg in range(start_deg, end_deg + 1):
            angle = math.radians(deg)
            idx = int(round((angle - msg.angle_min) / msg.angle_increment))
            idx %= len(msg.ranges)
            r = msg.ranges[idx]
            if math.isfinite(r) and r > msg.range_min:
                closest = min(closest, r)
        return closest

    def scan_callback(self, msg):
        front = self.sector_min(msg, -20, 20)
        left = self.sector_min(msg, 20, 90)
        right = self.sector_min(msg, -90, -20)

        cmd = TwistStamped()
        cmd.header.stamp = self.get_clock().now().to_msg()
        cmd.header.frame_id = 'base_link'

        if self.turn_dir != 0.0:
            # already turning: keep the same direction until clearly free
            if front > CLEAR_DISTANCE:
                self.turn_dir = 0.0
                cmd.twist.linear.x = FORWARD_SPEED
            else:
                cmd.twist.angular.z = self.turn_dir * TURN_SPEED
        elif front < SAFE_DISTANCE:
            self.turn_dir = 1.0 if left > right else -1.0
            cmd.twist.angular.z = self.turn_dir * TURN_SPEED
        else:
            cmd.twist.linear.x = FORWARD_SPEED

        self.publisher_.publish(cmd)

    def stop(self):
        cmd = TwistStamped()
        cmd.header.stamp = self.get_clock().now().to_msg()
        self.publisher_.publish(cmd)


def main(args=None):
    rclpy.init(args=args)
    node = ObstacleAvoider()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.stop()
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()