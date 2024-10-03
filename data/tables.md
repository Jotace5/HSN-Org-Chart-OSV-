# Database Schema Documentation

# ER Diagram

## Entities

### Office
- `id` (PK)
- `parentId` (FK to Office.id)
- `hierarchies`
- `officename`
- `currentRegulations`

### Official
- `id` (PK)
- `office_id` (FK to Office.id)
- `name`

## Relationships
- **Office** has a self-referencing one-to-many relationship via `parentId`.
- **Office** has a one-to-many relationship with **Official** via `office_id`.

## Tables

### Departments

| Column             | Data Type | Constraints                            | Description                                      |
|--------------------|-----------|----------------------------------------|--------------------------------------------------|
| `id`               | INTEGER   | PRIMARY KEY                            | Unique identifier for the department             |
| `parentId`         | INTEGER   | FOREIGN KEY REFERENCES Departments(`id`) | References the parent department's `id`          |
| `hierarchies`      | TEXT      | NOT NULL                               | Hierarchical level (e.g., A, B, C, etc.)         |
| `officename`       | TEXT      | NOT NULL                               | Name of the office                               |
| `official`         | TEXT      |                                        | Name of the official                             |
| `currentRegulations` | TEXT    |                                        | Current regulations associated with the office   |

---

## Relationships

- **Departments**
  - **parentId** is a foreign key referencing `Departments(id)`, establishing a hierarchical parent-child relationship between departments.

---

## Indexes

- **Primary Key Index**
  - `PRIMARY KEY` on `id` for unique identification and efficient querying.

- **Foreign Key Index**
  - Index on `parentId` to optimize hierarchical queries.

---

## Example Data

| id  | parentId | hierarchies | officename                                              | official                      | currentRegulations                        |
|-----|----------|-------------|---------------------------------------------------------|-------------------------------|--------------------------------------------|
| 100 |          | A           | Honorable Senado de la Nacion                           |                               |                                            |
| 101 | 100      | B           | Presidencia                                              | Dra. VILLARUEL VICTORIA       |                                            |
| 102 | 101      | E           | Dirección de Atención Ciudadana y Documentacón          | Juan Martín DONATO            | RSA 0198/20 - DP 0342/19- RSA 173/24        |
| ... | ...      | ...         | ...                                                     | ...                           | ...                                        |

---

## Notes

- Ensure that `parentId` values correspond to existing `id` entries to maintain referential integrity.
- `hierarchies` field represents the level in the organizational structure and can be used for sorting and display purposes.
- `currentRegulations` may contain multiple regulation codes separated by delimiters; consider normalizing if necessary.

