---
inclusion: fileMatch
fileMatchPattern: ['**/*.ts', '**/*.tsx']
---
# Rule: TypeScript Best Practices

## 1. Embrace Strict Type Safety
- The `any` type is strictly forbidden.
- Use `unknown` for data from external sources (e.g., API responses), and then use type guards (like `typeof`, `instanceof`, or custom type predicate functions) to narrow it down to a specific type before use.

## 2. Prefer `type` for Defining Shapes
- By default, use `type` aliases to define object shapes, unions, and intersections due to their consistency and flexibility.
- Use `interface` only when you need its specific features, such as declaration merging (e.g., augmenting third-party library types).

## 3. Leverage Type Inference
- Do not explicitly type variables or function return values when the type can be easily and accurately inferred by the compiler. Let TypeScript do the work.
    ```typescript
    // GOOD: Type is inferred as 'string'
    const userName = 'Vibe Coder';

    // BAD: Redundant typing
    const userName: string = 'Vibe Coder';
    ```

## 4. Use Specific and Precise Types
- Avoid generic types like `Function` or `object`. Define explicit function signatures.
- Use string literal union types instead of enums for simple, fixed sets of values. They are safer and provide better autocompletion.
    ```typescript
    // GOOD
    type Theme = 'light' | 'dark';

    // BAD
    enum Theme {
      Light,
      Dark
    }
    ```

## 5. Enforce Immutability
- Use the `readonly` keyword for properties that should not be changed after object creation.
- Use `Readonly<T>` and `ReadonlyArray<T>` for function arguments or states that should not be mutated.