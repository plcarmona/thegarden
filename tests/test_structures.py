"""
Tests for garden structure functionality
Validates point-in-polygon calculations and structure queries
"""
import pytest
import tempfile
import os
from database.kuzu_manager import KuzuDBManager


class TestStructures:
    """Tests for structure/polygon functionality"""
    
    def test_point_in_polygon(self):
        """Test point-in-polygon ray casting algorithm"""
        with tempfile.TemporaryDirectory() as temp_dir:
            db_path = os.path.join(temp_dir, "test.kuzu")
            manager = KuzuDBManager(db_path)
            
            # Test simple square polygon
            square = [[0, 0], [10, 0], [10, 10], [0, 10]]
            
            # Points inside
            assert manager._point_in_polygon(5, 5, square) == True
            assert manager._point_in_polygon(1, 1, square) == True
            assert manager._point_in_polygon(9, 9, square) == True
            
            # Points outside
            assert manager._point_in_polygon(-1, 5, square) == False
            assert manager._point_in_polygon(11, 5, square) == False
            assert manager._point_in_polygon(5, -1, square) == False
            assert manager._point_in_polygon(5, 11, square) == False
            
            # Points on border (behavior may vary by implementation)
            # We won't assert specific behavior for border cases
            
            # Test triangle
            triangle = [[0, 0], [10, 0], [5, 10]]
            
            assert manager._point_in_polygon(5, 3, triangle) == True  # Inside
            assert manager._point_in_polygon(1, 8, triangle) == False  # Outside
            assert manager._point_in_polygon(15, 5, triangle) == False  # Outside
            
            manager.close()
    
    def test_invalid_polygons(self):
        """Test behavior with invalid polygon data"""
        with tempfile.TemporaryDirectory() as temp_dir:
            db_path = os.path.join(temp_dir, "test.kuzu")
            manager = KuzuDBManager(db_path)
            
            # Empty polygon
            assert manager._point_in_polygon(5, 5, []) == False
            
            # Polygon with less than 3 vertices
            assert manager._point_in_polygon(5, 5, [[0, 0], [1, 1]]) == False
            
            # None polygon
            assert manager._point_in_polygon(5, 5, None) == False
            
            manager.close()
    
    def test_complex_polygon(self):
        """Test point-in-polygon with complex irregular polygon"""
        with tempfile.TemporaryDirectory() as temp_dir:
            db_path = os.path.join(temp_dir, "test.kuzu")
            manager = KuzuDBManager(db_path)
            
            # L-shaped polygon
            l_shape = [
                [0, 0],   # bottom-left
                [10, 0],  # bottom-middle
                [10, 5],  # middle-right
                [5, 5],   # middle-left
                [5, 10],  # top-right
                [0, 10]   # top-left
            ]
            
            # Points inside the L
            assert manager._point_in_polygon(2, 2, l_shape) == True
            assert manager._point_in_polygon(8, 2, l_shape) == True
            assert manager._point_in_polygon(2, 8, l_shape) == True
            
            # Points outside the L (in the cutout area)
            assert manager._point_in_polygon(8, 8, l_shape) == False
            
            # Points completely outside
            assert manager._point_in_polygon(-1, 5, l_shape) == False
            assert manager._point_in_polygon(15, 5, l_shape) == False
            
            manager.close()
    
    def test_structure_queries_without_kuzu(self):
        """Test that structure queries work gracefully without KuzuDB"""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create manager that can't connect to KuzuDB
            manager = KuzuDBManager(os.path.join(temp_dir, "test.kuzu"))
            manager._kuzu_available = False  # Force unavailable
            
            # Should return empty results gracefully
            assert manager.query_all_estructuras() == []
            assert manager.check_coordinate_in_structure(100, 100) == []
            
            manager.close()