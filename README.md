# Resource Segmentation

A Python library for intelligently grouping and segmenting resources with configurable overlap and boundary conditions.

## Overview

Resource Segmentation provides a flexible way to group resources based on their properties and constraints. It supports:

- **Hierarchical segmentation**: Resources can be grouped into segments based on boundary levels
- **Intelligent grouping**: Groups resources with configurable maximum counts and overlap ratios
- **Streaming processing**: Handles large datasets efficiently with iterator-based processing
- **Flexible boundary conditions**: Supports integer-based boundary levels for segmentation control

## Installation

```bash
pip install resource-segmentation
```

## Core Concepts

### Resources
Resources are the basic units that contain:
- `count`: The quantity/weight of the resource
- `start_incision`: The boundary level at the start (integer)
- `end_incision`: The boundary level at the end (integer)
- `payload`: Generic data associated with the resource

### Segments
Segments are collections of resources that can be grouped together based on compatible boundary levels.

### Groups
Groups are the final output containing:
- `head`: Optional overlapping resources from previous group
- `body`: Main resources in this group
- `tail`: Optional overlapping resources for next group
- `head_remain_count`/`tail_remain_count`: Remaining capacity in head/tail

## Usage Examples

### Basic Resource Grouping

```python
from resource_segmentation import split, Resource

# Create sample resources
resources = [
    Resource(100, 0, 0, "resource_0"),
    Resource(100, 0, 0, "resource_1"),
    Resource(100, 0, 0, "resource_2"),
    Resource(100, 0, 0, "resource_3"),
    Resource(100, 0, 0, "resource_4"),
]

# Group resources with max 400 per group and 25% overlap
groups = list(split(
    resources=iter(resources),
    max_segment_count=400,
    border_incision=0,
    gap_rate=0.25,
    tail_rate=0.5
))

# Process groups
for i, group in enumerate(groups):
    print(f"Group {i}:")
    print(f"  Body: {len(group.body)} items, total count: {sum(item.count for item in group.body)}")
    print(f"  Head overlap: {len(group.head)} items")
    print(f"  Tail overlap: {len(group.tail)} items")
```

### Segment-based Grouping

```python
from resource_segmentation import split, Resource, Segment

# Resources with different incision levels
resources = [
    Resource(100, 0, 0, 0),
    Resource(100, 0, 1, 0),
    Resource(100, 1, 1, 0),
    Resource(100, 1, 0, 0),
    Resource(100, 0, 0, 0),
]

# The middle three resources will be grouped into a segment
groups = list(split(
    resources=iter(resources),
    max_segment_count=1000,
    border_incision=0,
    gap_rate=0.0  # No overlap
))
```

### Handling Large Resources

```python
from resource_segmentation import split, Resource

# Mix of small and large resources
resources = [
    Resource(100, 0, 0, 0),
    Resource(300, 0, 0, 1),           # Large resource
    Resource(100, 0, 0, 2),
    Resource(100, 0, 0, 3),
]

# Group with max 400 per group - large resource will be handled appropriately
groups = list(split(
    resources=iter(resources),
    max_segment_count=400,
    border_incision=0,
    gap_rate=0.25,
    tail_rate=0.5
))
```

### Custom Overlap Distribution

```python
from resource_segmentation import split, Resource

resources = [
    Resource(400, 0, 0, 0),
    Resource(200, 0, 0, 1),
    Resource(400, 0, 0, 2),
]

# Distribute overlap mostly to tail (80% tail, 20% head)
groups = list(split(
    resources=iter(resources),
    max_segment_count=400,
    border_incision=0,
    gap_rate=0.25,
    tail_rate=0.8  # 80% to tail
))

# All overlap to tail
groups = list(split(
    resources=iter(resources),
    max_segment_count=400,
    border_incision=0,
    gap_rate=0.25,
    tail_rate=1.0  # 100% to tail
))
```

## API Reference

### Main Function

#### `split(resources, max_segment_count, border_incision, gap_rate=0.0, tail_rate=0.5)`

Groups resources into segments with configurable constraints.

**Parameters:**
- `resources` (Iterator[Resource[P]]): Iterator of resources to group
- `max_segment_count` (int): Maximum total count per segment
- `border_incision` (int): Border incision level for segmentation
- `gap_rate` (float, optional): Overlap ratio between groups (0.0-1.0). Default: 0.0
- `tail_rate` (float, optional): Distribution ratio for overlap (0.0-1.0). Default: 0.5

**Yields:**
- `Group[P]`: Grouped resources with head, body, tail sections

### Data Types

#### `Resource[P]`
```python
@dataclass
class Resource(Generic[P]):
    count: int                    # Resource quantity
    start_incision: int          # Start boundary level
    end_incision: int            # End boundary level
    payload: P                   # Associated data
```

#### `Segment[P]`
```python
@dataclass
class Segment(Generic[P]):
    count: int                   # Total count of contained resources
    resources: list[Resource[P]] # List of resources in segment
```

#### `Group[P]`
```python
@dataclass
class Group(Generic[P]):
    head_remain_count: int                    # Remaining head capacity
    tail_remain_count: int                    # Remaining tail capacity
    head: list[Resource[P] | Segment[P]]     # Head section (overlap)
    body: list[Resource[P] | Segment[P]]     # Main body section
    tail: list[Resource[P] | Segment[P]]     # Tail section (overlap)
```

### Boundary Levels

The library uses integer boundary levels to determine how resources can be segmented. Higher values indicate stronger boundary conditions.

## Testing

Run the test suite:

```bash
python test.py
```

## License

This project is licensed under the MIT License.