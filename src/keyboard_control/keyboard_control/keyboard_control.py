import sys
import threading

import geometry_msgs.msg
import rclpy

import termios
import tty
import time


msg = """
Press these keys to control your turtlebot
---------------------------
Moving around:
        W    
   A    G    D
        S    

        
CTRL-C to quit
"""

def getKey(settings):
        tty.setraw(sys.stdin.fileno())
        key = sys.stdin.read(1)
        termios.tcsetattr(sys.stdin, termios.TCSADRAIN, settings)
        return key


def saveTerminalSettings():
    return termios.tcgetattr(sys.stdin)


def restoreTerminalSettings(old_settings):
    termios.tcsetattr(sys.stdin, termios.TCSADRAIN, old_settings)



def main():
    settings = saveTerminalSettings()

    rclpy.init()

    node = rclpy.create_node('control_turtlebot_node')
    stamped = node.declare_parameter('stamped', False).value
    frame_id = node.declare_parameter('frame_id', '').value
    if not stamped and frame_id:
        raise Exception("'frame_id' can only be set when 'stamped' is True")

    if stamped:
        TwistMsg = geometry_msgs.msg.TwistStamped
    else:
        TwistMsg = geometry_msgs.msg.Twist

    pub = node.create_publisher(TwistMsg, 'cmd_vel', 10)

    spinner = threading.Thread(target=rclpy.spin, args=(node,))
    spinner.start()

    turn = 1.0
    x = 0.0
    y = 0.0
    z = 0.0
    th = 0.0

    twist_msg = TwistMsg()

    if stamped:
        twist = twist_msg.twist
        twist_msg.header.stamp = node.get_clock().now().to_msg()
        twist_msg.header.frame_id = frame_id
    else:
        twist = twist_msg

    try:
        print(msg)
        while True:
            key = getKey(settings)
            match key:
                case "w":
                    x=1
                    y=0
                    z=0
                    th=0
                    print(f'going forward')
                case "s":
                    x=-1
                    y=0
                    z=0
                    th=0
                    print(f'going back')
                case "a":
                    x = 0
                    y = 0
                    z = 0
                    th = 1
                    print(f'turning left')
                case "d":
                    x = 0
                    y = 0
                    z = 0
                    th = -1
                    print(f'Turning right')
                case "g":
                    x=0
                    y=0
                    z=0
                    th=0
                    print(f'Stopping turtlebot!')
                case '\x03':
                    break
                case _:
                    x=0
                    y=0
                    z=0
                    th=0

            if stamped:
                twist_msg.header.stamp = node.get_clock().now().to_msg()

            twist.linear.x = x*0.3
            twist.linear.y = y*0.3
            twist.linear.z = z*0.3
            twist.angular.x = 0.0
            twist.angular.y = 0.0
            twist.angular.z = th * turn
            pub.publish(twist_msg)
            time.sleep(0.5)
            twist.linear.x = 0.0
            twist.linear.y = 0.0
            twist.linear.z = 0.0
            twist.angular.x = 0.0
            twist.angular.y = 0.0
            twist.angular.z = 0 * turn
            pub.publish(twist_msg)

    except Exception as e:
        print(e)

    finally:
        if stamped:
            twist_msg.header.stamp = node.get_clock().now().to_msg()

        twist.linear.x = 0.0
        twist.linear.y = 0.0
        twist.linear.z = 0.0
        twist.angular.x = 0.0
        twist.angular.y = 0.0
        twist.angular.z = 0.0
        pub.publish(twist_msg)
        rclpy.shutdown()
        spinner.join()

        restoreTerminalSettings(settings)


if __name__ == '__main__':
    main()
