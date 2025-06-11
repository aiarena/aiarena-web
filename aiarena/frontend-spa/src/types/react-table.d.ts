// types/react-table.d.ts
import '@tanstack/react-table';

declare module '@tanstack/react-table' {
    interface ColumnMeta {
        priority?: number;
    }
}