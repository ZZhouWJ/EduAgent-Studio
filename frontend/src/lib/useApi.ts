import { useEffect, useState, useCallback } from 'react'
import client, { ApiError } from './api/client'

export interface UseApiState<T> {
  data: T | null
  loading: boolean
  error: ApiError | null
}

export interface UseApiResult<T, P extends unknown[] = []> extends UseApiState<T> {
  refetch: (...args: P) => Promise<void>
}

export function useApi<T, P extends unknown[] = []>(
  fetcher: (...args: P) => Promise<T>,
  deps: ReadonlyArray<unknown> = [],
): UseApiResult<T, P> {
  const [state, setState] = useState<UseApiState<T>>({ data: null, loading: true, error: null })

  const run = useCallback(async (...args: P) => {
    setState((s) => ({ ...s, loading: true, error: null }))
    try {
      const data = await fetcher(...args)
      setState({ data, loading: false, error: null })
    } catch (e) {
      setState({ data: null, loading: false, error: e instanceof ApiError ? e : new ApiError(String(e), -1) })
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, deps)

  useEffect(() => {
    run(...([] as unknown as P))
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, deps)

  return { ...state, refetch: run }
}

export { client }
