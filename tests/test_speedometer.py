"""Tests for the Speedometer class."""

import matplotlib.pyplot as plt
import pytest

from mplsoccer import Speedometer


class TestSpeedometer:
    """Tests for Speedometer class."""

    def test_speedometer_creation(self):
        """Test basic instantiation without errors."""
        speedo = Speedometer(start_value=0, end_value=10)
        assert speedo.start_value == 0
        assert speedo.end_value == 10
        assert speedo.radius == 4  # default value

    def test_speedometer_draw_returns_fig_ax(self):
        """Test that draw() returns (fig, ax) when ax=None."""
        speedo = Speedometer(start_value=0, end_value=10)
        result = speedo.draw(value=5)
        assert result is not None
        assert len(result) == 2
        fig, ax = result
        assert isinstance(fig, plt.Figure)
        assert hasattr(ax, 'plot')  # verify it's an axes object
        plt.close(fig)

    def test_speedometer_draw_with_ax(self):
        """Test that draw(ax=ax) returns None."""
        speedo = Speedometer(start_value=0, end_value=10)
        fig, ax = plt.subplots()
        result = speedo.draw(value=5, ax=ax)
        assert result is None
        plt.close(fig)

    def test_speedometer_value_bounds(self):
        """Test values at min/max/out-of-range don't crash."""
        speedo = Speedometer(start_value=0, end_value=10)
        
        # Value at minimum
        fig, ax = speedo.draw(value=0)
        plt.close(fig)
        
        # Value at maximum
        fig, ax = speedo.draw(value=10)
        plt.close(fig)
        
        # Value below minimum
        fig, ax = speedo.draw(value=-5)
        plt.close(fig)
        
        # Value above maximum
        fig, ax = speedo.draw(value=15)
        plt.close(fig)

    def test_speedometer_custom_colors(self):
        """Test custom color list works."""
        custom_colors = ["#ff0000", "#00ff00", "#0000ff"]
        speedo = Speedometer(
            start_value=0,
            end_value=10,
            colors=custom_colors
        )
        assert speedo.colors == custom_colors
        assert speedo.n_colors == 3
        
        fig, ax = speedo.draw(value=5)
        plt.close(fig)

    def test_speedometer_repr(self):
        """Test __repr__ returns string."""
        speedo = Speedometer(start_value=0, end_value=10)
        repr_str = repr(speedo)
        assert isinstance(repr_str, str)
        assert "Speedometer" in repr_str
        assert "start_value=0" in repr_str
        assert "end_value=10" in repr_str

    def test_speedometer_with_title_and_unit(self):
        """Test speedometer with title and unit."""
        speedo = Speedometer(
            start_value=0,
            end_value=12,
            title="Player Speed",
            unit=" m/s"
        )
        fig, ax = speedo.draw(value=8.5)
        plt.close(fig)

    def test_speedometer_custom_angles(self):
        """Test custom start and end angles."""
        speedo = Speedometer(
            start_value=0,
            end_value=10,
            start_angle=0,
            end_angle=180
        )
        assert speedo.start_angle == 0
        assert speedo.end_angle == 180
        
        fig, ax = speedo.draw(value=5)
        plt.close(fig)

    def test_speedometer_no_labels(self):
        """Test speedometer without labels."""
        speedo = Speedometer(
            start_value=0,
            end_value=10,
            draw_labels=False
        )
        fig, ax = speedo.draw(value=5)
        plt.close(fig)

    def test_speedometer_no_annotation(self):
        """Test speedometer without annotation."""
        speedo = Speedometer(
            start_value=0,
            end_value=10,
            draw_annotation=False
        )
        fig, ax = speedo.draw(value=5)
        plt.close(fig)

    def test_speedometer_invalid_range(self):
        """Test that invalid range raises ValueError."""
        with pytest.raises(ValueError, match="end_value must be greater than start_value"):
            Speedometer(start_value=10, end_value=5)
        
        with pytest.raises(ValueError, match="end_value must be greater than start_value"):
            Speedometer(start_value=5, end_value=5)

    def test_speedometer_empty_colors(self):
        """Test that empty colors list raises ValueError."""
        with pytest.raises(ValueError, match="colors list cannot be empty"):
            Speedometer(start_value=0, end_value=10, colors=[])

    def test_speedometer_invalid_radius(self):
        """Test that non-positive radius raises ValueError."""
        with pytest.raises(ValueError, match="radius must be positive"):
            Speedometer(start_value=0, end_value=10, radius=0)
        
        with pytest.raises(ValueError, match="radius must be positive"):
            Speedometer(start_value=0, end_value=10, radius=-1)
