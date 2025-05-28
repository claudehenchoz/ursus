#!/usr/bin/env python3
"""Profiling script to measure application startup performance."""

import cProfile
import pstats
import time
import sys
import os

# Add the ursus package to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def profile_startup():
    """Profile the application startup."""
    print("Profiling application startup...")
    
    # Profile with cProfile
    profiler = cProfile.Profile()
    profiler.enable()
    
    start_time = time.time()
    
    # Import and initialize the application
    from ursus.main_window import MainWindow
    from PySide6.QtWidgets import QApplication
    
    app = QApplication(sys.argv)
    window = MainWindow(text_size=20)
    
    init_time = time.time()
    
    # Show window (this triggers final UI setup)
    window.show()
    
    show_time = time.time()
    
    profiler.disable()
    
    # Print timing results
    print(f"\nTiming Results:")
    print(f"Import + Init: {(init_time - start_time)*1000:.2f}ms")
    print(f"Show window: {(show_time - init_time)*1000:.2f}ms")
    print(f"Total startup: {(show_time - start_time)*1000:.2f}ms")
    
    # Save profiling results
    profiler.dump_stats('startup_profile.prof')
    
    # Print top functions by cumulative time
    stats = pstats.Stats(profiler)
    print("\nTop 20 functions by cumulative time:")
    stats.sort_stats('cumulative').print_stats(20)
    
    print("\nTop 20 functions by self time:")
    stats.sort_stats('tottime').print_stats(20)
    
    # Close the app
    app.quit()

def simple_timing_test():
    """Simple timing test without QApplication conflicts."""
    print("\nSimple timing test...")
    
    # Time just the import and initialization
    start = time.time()
    
    from ursus.main_window import MainWindow
    from PySide6.QtWidgets import QApplication
    
    init_time = time.time()
    print(f"Import time: {(init_time - start)*1000:.2f}ms")
    
    # Create app and window
    app = QApplication.instance() or QApplication(sys.argv)
    window = MainWindow(text_size=20)
    
    create_time = time.time()
    print(f"Window creation: {(create_time - init_time)*1000:.2f}ms")
    
    window.show()
    
    show_time = time.time()
    print(f"Show window: {(show_time - create_time)*1000:.2f}ms")
    print(f"Total optimized startup: {(show_time - start)*1000:.2f}ms")
    
    return show_time - start

if __name__ == "__main__":
    profile_startup()
    simple_timing_test()