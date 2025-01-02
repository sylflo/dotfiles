import cairo
import math
import time
import os
import uuid

def draw_clock(output_path: str):
    WIDTH, HEIGHT = 300, 300  # Adjust size for your use case
    surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, WIDTH, HEIGHT)
    ctx = cairo.Context(surface)

    # Transparent background
    ctx.set_source_rgba(0, 0, 0, 0)  # Fully transparent
    ctx.rectangle(0, 0, WIDTH, HEIGHT)
    ctx.fill()

    # Center and radius
    center_x, center_y = WIDTH / 2, HEIGHT / 2
    radius = WIDTH / 2 - 10

    # Draw clock face (thin circle)
    ctx.set_source_rgb(1, 1, 1)  # White color
    ctx.set_line_width(2)
    ctx.arc(center_x, center_y, radius, 0, 2 * math.pi)
    ctx.stroke()

    # Draw clock ticks (12-hour markers)
    for i in range(12):
        angle = i * math.pi / 6  # 12 ticks, 360° / 12 = 30°
        x1 = center_x + math.cos(angle) * (radius - 10)
        y1 = center_y + math.sin(angle) * (radius - 10)
        x2 = center_x + math.cos(angle) * radius
        y2 = center_y + math.sin(angle) * radius
        ctx.set_line_width(2)
        ctx.move_to(x1, y1)
        ctx.line_to(x2, y2)
        ctx.stroke()

    # Get current time
    now = time.localtime()
    hours, minutes, seconds = now.tm_hour % 12, now.tm_min, now.tm_sec

    # Draw hour hand
    hour_angle = (hours + minutes / 60) * math.pi / 6
    ctx.set_line_width(6)
    ctx.move_to(center_x, center_y)
    ctx.line_to(
        center_x + math.cos(hour_angle - math.pi / 2) * (radius * 0.5),
        center_y + math.sin(hour_angle - math.pi / 2) * (radius * 0.5),
    )
    ctx.stroke()

    # Draw minute hand
    minute_angle = (minutes + seconds / 60) * math.pi / 30
    ctx.set_line_width(4)
    ctx.move_to(center_x, center_y)
    ctx.line_to(
        center_x + math.cos(minute_angle - math.pi / 2) * (radius * 0.75),
        center_y + math.sin(minute_angle - math.pi / 2) * (radius * 0.75),
    )
    ctx.stroke()

    # Save the image
    surface.write_to_png(output_path)



random_filename = "modern_clock.png"
file_path = os.path.join("/home/sylflo/.config/hypr/scripts/clock", random_filename)
#raise Exception(file_path)

# Call draw_clock with the random filename
draw_clock(file_path)
print(random_filename)


# if __name__ == "__main__":
#     random_filename = "./modern_clock.png"
#     file_path = os.path.join("clock", random_filename)
    
#     # Call draw_clock with the random filename
#     draw_clock(file_path)
#     print(random_filename)

# if __name__ == "__main__":
#     # Ensure the 'clock' folder exists
#     os.makedirs("clock", exist_ok=True)
    
#     # Generate a random filename
#     random_filename = f"{uuid.uuid4().hex}.png"
#     file_path = os.path.join("clock", random_filename)
    
#     # Call draw_clock with the random filename
#     draw_clock(file_path)
#     print(random_filename)