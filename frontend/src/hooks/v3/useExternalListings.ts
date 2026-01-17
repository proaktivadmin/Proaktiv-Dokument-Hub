"use client";

import { useState, useEffect, useCallback } from 'react';
import { externalListingsApi, type ExternalListingListParams } from '@/lib/api/external-listings';
import type { ExternalListing, ListingSource, ListingStatus } from '@/types/v3';

export function useExternalListings(params?: ExternalListingListParams) {
  const [listings, setListings] = useState<ExternalListing[]>([]);
  const [total, setTotal] = useState(0);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetch = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    try {
      const data = await externalListingsApi.list(params);
      setListings(data.items);
      setTotal(data.total);
    } catch (err) {
      console.error('[useExternalListings] Error:', err);
      setError(err instanceof Error ? err.message : 'Failed to fetch external listings');
    } finally {
      setIsLoading(false);
    }
  }, [params?.office_id, params?.employee_id, params?.source, params?.status, params?.skip, params?.limit]);

  useEffect(() => {
    fetch();
  }, [fetch]);

  // Group by status
  const byStatus = listings.reduce((acc, listing) => {
    const status = listing.status;
    if (!acc[status]) acc[status] = [];
    acc[status].push(listing);
    return acc;
  }, {} as Record<ListingStatus, ExternalListing[]>);

  // Group by source
  const bySource = listings.reduce((acc, listing) => {
    const source = listing.source;
    if (!acc[source]) acc[source] = [];
    acc[source].push(listing);
    return acc;
  }, {} as Record<ListingSource, ExternalListing[]>);

  // Needs attention count
  const needsAttentionCount = listings.filter(l => l.needs_attention).length;

  return { 
    listings, 
    total,
    byStatus,
    bySource,
    needsAttentionCount,
    isLoading, 
    error, 
    refetch: fetch 
  };
}

export function useExternalListing(id: string | null) {
  const [listing, setListing] = useState<ExternalListing | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetch = useCallback(async () => {
    if (!id) {
      setListing(null);
      return;
    }

    setIsLoading(true);
    setError(null);
    try {
      const data = await externalListingsApi.get(id);
      setListing(data);
    } catch (err) {
      console.error('[useExternalListing] Error:', err);
      setError(err instanceof Error ? err.message : 'Failed to fetch external listing');
    } finally {
      setIsLoading(false);
    }
  }, [id]);

  useEffect(() => {
    fetch();
  }, [fetch]);

  const verify = useCallback(async (notes?: string) => {
    if (!id) return;
    try {
      const updated = await externalListingsApi.verify(id, notes);
      setListing(updated);
      return updated;
    } catch (err) {
      console.error('[useExternalListing] Verify error:', err);
      throw err;
    }
  }, [id]);

  return { listing, isLoading, error, refetch: fetch, verify };
}
