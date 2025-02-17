from pynput import mouse, keyboard
import threading
import time
import pygetwindow as gw

scroll_enabled = False
caps_lock_pressed = False
start_y = 0
click_count = 0
last_click_time = 0
lock = threading.Lock()

def is_active_window():
    active_window = gw.getActiveWindow()
    return active_window is not None

def on_click(x, y, button, pressed):
    global scroll_enabled, start_y, click_count, last_click_time
    
    if pressed :
        if button == mouse.Button.left:
            click_count += 1
            current_time = time.time()
            if click_count == 1:
                last_click_time = current_time
            elif click_count == 2 and (current_time - last_click_time) <= 0.3:
                click_count = 0
                scroll_enabled = caps_lock_pressed and is_active_window()
        else:
            click_count = 1

        if caps_lock_pressed and is_active_window():
            scroll_enabled = True
            start_y = y
        else:
            scroll_enabled = False

def on_press(key):
    global caps_lock_pressed, scroll_enabled
    if key == keyboard.Key.caps_lock:
        caps_lock_pressed = True
    
    with lock :    
        if key == keyboard.Key.esc:
            scroll_enabled = False

def on_release(key):
    global scroll_enabled, caps_lock_pressed
    with lock :
        if key == keyboard.Key.caps_lock:
            scroll_enabled = False
            caps_lock_pressed = False
    

def scroll_mouse():
    global start_y

    while True:
        with lock :
            if scroll_enabled and caps_lock_pressed and is_active_window():
                current_y = mouse.Controller().position[1]
                delta_y = current_y - start_y

                if delta_y != 0:
                    # 可以在delta_y前添加 - 实现反向滚动，通过调节除数控制滚动速度，越大越慢。
                    mouse.Controller().scroll(0, delta_y / 20)
                start_y = current_y
            
        time.sleep(0.01)



mouse_listener = mouse.Listener(on_click=on_click)
keyboard_listener = keyboard.Listener(on_press=on_press, on_release=on_release)

mouse_listener.start()
keyboard_listener.start()

scroll_thread = threading.Thread(target=scroll_mouse, daemon=True)
scroll_thread.start()

keyboard_listener.join()
mouse_listener.join()