"use client";

import { useState, useEffect, useCallback } from 'react';
import { assetsApi, type AssetListParams } from '@/lib/api/assets';
import type { CompanyAsset, AssetCategory } from '@/types/v3';

export function useAssets(params?: AssetListParams) {
  const [assets, setAssets] = useState<CompanyAsset[]>([]);
  const [total, setTotal] = useState(0);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetch = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    try {
      const data = await assetsApi.list(params);
      setAssets(data.items);
      setTotal(data.total);
    } catch (err) {
      console.error('[useAssets] Error:', err);
      setError(err instanceof Error ? err.message : 'Failed to fetch assets');
    } finally {
      setIsLoading(false);
    }
  }, [params?.category, params?.office_id, params?.employee_id, params?.is_global, params?.skip, params?.limit]);

  useEffect(() => {
    fetch();
  }, [fetch]);

  // Group by category
  const byCategory = assets.reduce((acc, asset) => {
    const cat = asset.category;
    if (!acc[cat]) acc[cat] = [];
    acc[cat].push(asset);
    return acc;
  }, {} as Record<AssetCategory, CompanyAsset[]>);

  // Category counts
  const categoryCounts: Record<AssetCategory, number> = {
    logo: byCategory.logo?.length || 0,
    photo: byCategory.photo?.length || 0,
    marketing: byCategory.marketing?.length || 0,
    document: byCategory.document?.length || 0,
    other: byCategory.other?.length || 0,
  };

  return { 
    assets, 
    total,
    byCategory,
    categoryCounts,
    isLoading, 
    error, 
    refetch: fetch 
  };
}

export function useAsset(id: string | null) {
  const [asset, setAsset] = useState<CompanyAsset | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetch = useCallback(async () => {
    if (!id) {
      setAsset(null);
      return;
    }

    setIsLoading(true);
    setError(null);
    try {
      const data = await assetsApi.get(id);
      setAsset(data);
    } catch (err) {
      console.error('[useAsset] Error:', err);
      setError(err instanceof Error ? err.message : 'Failed to fetch asset');
    } finally {
      setIsLoading(false);
    }
  }, [id]);

  useEffect(() => {
    fetch();
  }, [fetch]);

  return { asset, isLoading, error, refetch: fetch };
}
