"""
Latent-FS - The Vector File System
Author: Gary Dev of Xanthorox
Copyright © 2026 Xanthorox

Tests for debouncing functionality in re-embedding endpoint.
"""

import pytest
import time
from backend.api.routes import should_perform_reclustering
from backend.config import settings
import backend.api.routes as routes


def test_should_perform_reclustering_allows_first_call():
    """Test that the first call to should_perform_reclustering returns True."""
    # Reset the global state
    routes.last_reclustering_time = 0.0
    
    # First call should always be allowed
    result = should_perform_reclustering()
    assert result is True, "First re-clustering call should be allowed"


def test_should_perform_reclustering_blocks_rapid_calls():
    """Test that rapid calls within debounce window are blocked."""
    # Reset the global state
    routes.last_reclustering_time = 0.0
    
    # First call should be allowed
    result1 = should_perform_reclustering()
    assert result1 is True, "First call should be allowed"
    
    # Immediate second call should be blocked
    result2 = should_perform_reclustering()
    assert result2 is False, "Second call within debounce window should be blocked"
    
    # Third call immediately after should also be blocked
    result3 = should_perform_reclustering()
    assert result3 is False, "Third call within debounce window should be blocked"


def test_should_perform_reclustering_allows_after_window():
    """Test that calls after debounce window are allowed."""
    # Reset the global state
    routes.last_reclustering_time = 0.0
    
    # First call
    result1 = should_perform_reclustering()
    assert result1 is True, "First call should be allowed"
    
    # Wait for debounce window to expire
    time.sleep(settings.DEBOUNCE_WINDOW_SECONDS + 0.1)
    
    # Call after window should be allowed
    result2 = should_perform_reclustering()
    assert result2 is True, "Call after debounce window should be allowed"


def test_debouncing_prevents_excessive_operations():
    """
    Test Property 13: For any sequence of N rapid embedding modifications,
    the system should perform fewer than N clustering operations.
    """
    # Reset the global state
    routes.last_reclustering_time = 0.0
    
    n_modifications = 10
    allowed_count = 0
    blocked_count = 0
    
    # Perform rapid calls
    for i in range(n_modifications):
        if should_perform_reclustering():
            allowed_count += 1
        else:
            blocked_count += 1
        
        # Small delay between calls (simulating rapid user actions)
        time.sleep(0.1)
    
    print(f"\nOut of {n_modifications} rapid calls:")
    print(f"  Allowed: {allowed_count}")
    print(f"  Blocked: {blocked_count}")
    
    # With debouncing, we should have fewer allowed operations than total modifications
    assert allowed_count < n_modifications, \
        f"Debouncing should prevent some operations: {allowed_count} >= {n_modifications}"
    
    # We should have blocked at least some operations
    assert blocked_count > 0, "Debouncing should block at least some operations"
    
    print(f"  ✓ Debouncing prevented {blocked_count} excessive operations")


def test_debouncing_thread_safety():
    """Test that debouncing is thread-safe with concurrent calls."""
    import threading
    
    # Reset the global state
    routes.last_reclustering_time = 0.0
    
    results = []
    
    def make_call():
        result = should_perform_reclustering()
        results.append(result)
    
    # Create multiple threads that call simultaneously
    threads = []
    for i in range(5):
        thread = threading.Thread(target=make_call)
        threads.append(thread)
    
    # Start all threads at once
    for thread in threads:
        thread.start()
    
    # Wait for all threads to complete
    for thread in threads:
        thread.join()
    
    # Only one thread should have been allowed (the first one)
    allowed_count = sum(1 for r in results if r is True)
    blocked_count = sum(1 for r in results if r is False)
    
    print(f"\nConcurrent calls:")
    print(f"  Allowed: {allowed_count}")
    print(f"  Blocked: {blocked_count}")
    
    # With thread-safe locking, only one should be allowed
    assert allowed_count == 1, \
        f"Only one concurrent call should be allowed, got {allowed_count}"
    assert blocked_count == 4, \
        f"Four concurrent calls should be blocked, got {blocked_count}"


def test_debounce_window_configuration():
    """Test that the debounce window is properly configured."""
    assert hasattr(settings, 'DEBOUNCE_WINDOW_SECONDS'), \
        "Settings should have DEBOUNCE_WINDOW_SECONDS"
    
    assert settings.DEBOUNCE_WINDOW_SECONDS > 0, \
        "Debounce window should be positive"
    
    assert settings.DEBOUNCE_WINDOW_SECONDS <= 10, \
        "Debounce window should be reasonable (not too long)"
    
    print(f"\n✓ Debounce window configured: {settings.DEBOUNCE_WINDOW_SECONDS}s")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
