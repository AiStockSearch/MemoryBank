# useMyCustomHook (snapshot 2024-06-20)

**Описание:**
Хук для управления состоянием X в компоненте Y. Используется для ...

**Контекст:**
- Проект: client-x
- Компонент: SomeComponent.tsx
- Причина снапшота: стабильная версия для задачи Z, требуется для передачи/отката/рефакторинга
- Автор: <ваше имя или команда>
- Дата: 2024-06-20

---

## Код
```ts
export function useMyCustomHook() {
  // ... код хука ...
}
```

---

## Тесты
```ts
import { renderHook } from '@testing-library/react-hooks';

describe('useMyCustomHook', () => {
  it('должен возвращать ...', () => {
    const { result } = renderHook(() => useMyCustomHook());
    // ... тесты ...
  });
});
```

---

## Usage
```tsx
import { useMyCustomHook } from './useMyCustomHook';

function SomeComponent() {
  const value = useMyCustomHook();
  // ...
}
```

---

## История изменений
- 2024-06-20: Снапшот создан для задачи Z
- ... 