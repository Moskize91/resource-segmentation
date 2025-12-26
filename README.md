<div align=center>
  <h1>Resource Segmentation</h1>
  <p>
    <a href="https://github.com/Moskize91/resource-segmentation/actions/workflows/pr-check.yml" target="_blank"><img src="https://img.shields.io/github/actions/workflow/status/Moskize91/resource-segmentation/pr-check.yml" alt="ci" /></a>
    <a href="https://pypi.org/project/resource-segmentation/" target="_blank"><img src="https://img.shields.io/badge/pip_install-resource--segmentation-blue" alt="pip install resource-segmentation" /></a>
    <a href="https://pypi.org/project/resource-segmentation/" target="_blank"><img src="https://img.shields.io/pypi/v/resource-segmentation.svg" alt="pypi resource-segmentation" /></a>
    <a href="https://pypi.org/project/resource-segmentation/" target="_blank"><img src="https://img.shields.io/pypi/pyversions/resource-segmentation.svg" alt="python versions" /></a>
    <a href="https://github.com/Moskize91/resource-segmentation/blob/main/LICENSE" target="_blank"><img src="https://img.shields.io/github/license/Moskize91/resource-segmentation" alt="license" /></a>
  </p>
</div>

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
- `head`: Optional overlapping resources from previous group (automatically truncated)
- `body`: Main resources in this group
- `tail`: Optional overlapping resources for next group (automatically truncated)
- `head_remain_count`/`tail_remain_count`: Maximum allowed count for head/tail (may be less than actual total if resources are indivisible)

**Gap Truncation**: The library automatically truncates head and tail to optimize overlap:
- `head` is truncated from back to front (keeping resources closer to body)
- `tail` is truncated from front to back (keeping resources closer to body)
- `remain_count` values indicate the **effective limit**, not necessarily the actual sum
- Since resources are indivisible, actual totals in head/tail may exceed `remain_count`
- This design alerts users to manually truncate if needed while respecting resource boundaries

## Usage Examples

### Basic Resource Grouping

```python
from resource_segmentation import split, Resource

# Create sample resources
resources = [
    Resource(100, 0, 0, 0),
    Resource(100, 0, 0, 1),
    Resource(100, 0, 0, 2),
    Resource(100, 0, 0, 3),
    Resource(100, 0, 0, 4),
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
    print(f"  Head: {len(group.head)} items (remain_count: {group.head_remain_count})")
    print(f"  Tail: {len(group.tail)} items (remain_count: {group.tail_remain_count})")
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
    Resource(300, 0, 0, 1), # Large resource
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
- `max_segment_count` (int): Maximum total count per segment (including head, body, and tail)
- `border_incision` (int): Border incision level for segmentation
- `gap_rate` (float, optional): Overlap ratio between groups (0.0-1.0). Default: 0.0
  - The gap (overlap) is calculated as `floor(max_segment_count * gap_rate)`
  - The body max count is `max_segment_count - gap * 2`
- `tail_rate` (float, optional): Distribution ratio for overlap (0.0-1.0). Default: 0.5
  - 0.0 means all overlap goes to head, 1.0 means all overlap goes to tail

**Yields:**
- `Group[P]`: Grouped resources with head, body, tail sections
  - Head and tail are automatically truncated based on `gap_rate` and `tail_rate`
  - `head_remain_count`/`tail_remain_count` indicate the maximum allowed count (effective limits)
  - Actual totals may exceed these limits when resources cannot be divided

### Data Types

#### `Resource[P]`
```python
@dataclass
class Resource(Generic[P]):
    count: int                   # Resource quantity
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
    head_remain_count: int                   # Maximum allowed count for head (effective limit)
    tail_remain_count: int                   # Maximum allowed count for tail (effective limit)
    head: list[Resource[P] | Segment[P]]     # Head section (overlap, truncated)
    body: list[Resource[P] | Segment[P]]     # Main body section
    tail: list[Resource[P] | Segment[P]]     # Tail section (overlap, truncated)
```

### Boundary Levels

The library uses integer boundary levels to determine how resources can be segmented. Higher values indicate stronger boundary conditions.

## Development

### Setup

First, install dependencies using Poetry:

```bash
poetry install
```

### Testing

Run the test suite:

```bash
python test.py
```

## License

This project is licensed under the MIT License.