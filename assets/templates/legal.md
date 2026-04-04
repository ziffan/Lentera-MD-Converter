---
title: "{{ title }}"
source: "{{ source_file }}"
date: "{{ date }}"
word_count: {{ word_count }}
generated_by: Lentera MD
---

# {{ title }}

## Metadata Dokumen
- **Sumber**: {{ source }}
- **Tanggal**: {{ date }}
- **Jumlah Halaman**: {{ page_count }}
- **Jumlah Kata**: {{ word_count }}

---

{{ content }}
