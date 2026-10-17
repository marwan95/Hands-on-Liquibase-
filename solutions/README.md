# Solutions ⚠️ spoilers

Try each module (hands-on + quiz) and run the grader **before** you open these.

| Module | Explanations | Reference files |
|---|---|---|
| 00 Setup & concepts | [module-00.md](module-00.md) | – |
| 01 First deployment | [module-01.md](module-01.md) | [module01.sql](lab/changelog/module01.sql) |
| 02 Formats & structure | [module-02.md](module-02.md) | [module02.yaml](lab/changelog/module02.yaml), [module02.xml](lab/changelog/module02.xml) |
| 03 Change types | [module-03.md](module-03.md) | [module03.yaml](lab/changelog/module03.yaml), [module03_routines.sql](lab/changelog/module03_routines.sql) |
| 04 Rollbacks & tags | [module-04.md](module-04.md) | [module04.yaml](lab/changelog/module04.yaml) |
| 05 Checksums & run modes | [module-05.md](module-05.md) | [module05.sql](lab/changelog/module05.sql) |
| 06 Preconditions | [module-06.md](module-06.md) | [module06.sql](lab/changelog/module06.sql) |
| 07 Contexts, labels & parameters | [module-07.md](module-07.md) | [module07.sql](lab/changelog/module07.sql), [liquibase.properties](lab/liquibase.properties) |
| 08 Oracle & cross-database | [module-08.md](module-08.md) | all `*.sql` files (the `-ora` twins), [liquibase-oracle.properties](lab/liquibase-oracle.properties) |
| 09 Reverse engineering & drift | [module-09.md](module-09.md) | [legacy/](lab/changelog/legacy) |
| 10 Data engineering patterns | [module-10.md](module-10.md) | [module10.yaml](lab/changelog/module10.yaml), [country_codes.csv](lab/changelog/data/country_codes.csv) |
| 11 Final exam | [module-exam.md](module-exam.md) | [exam.sql](lab/changelog/exam.sql) |

`lab/` here shows the **final state** of the learner's lab after the whole course, including the Module 08 changes (`dbms:` attributes and `-ora` twins) in the earlier files. It was played through module by module against fresh containers and scores **114/114** with the grader.

> The changesets use `student` as the author. Yours will have your own name, which is fine: the grader checks database state, not authors.
