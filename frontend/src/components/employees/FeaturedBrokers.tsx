"use client";

import Link from "next/link";
import { Facebook, Instagram, Linkedin, Twitter } from "lucide-react";
import { useEmployees } from "@/hooks/v3/useEmployees";
import { Card, CardContent } from "@/components/ui/card";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import { Skeleton } from "@/components/ui/skeleton";
import { resolveAvatarUrl } from "@/lib/api/config";

interface FeaturedBrokersProps {
  officeId: string;
}

export function FeaturedBrokers({ officeId }: FeaturedBrokersProps) {
  const { employees, isLoading } = useEmployees({ office_id: officeId, is_featured: true });

  if (isLoading) {
    return (
      <section className="mb-6">
        <Skeleton className="h-6 w-48 mb-3" />
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {Array.from({ length: 3 }).map((_, index) => (
            <Skeleton key={index} className="h-28" />
          ))}
        </div>
      </section>
    );
  }

  if (employees.length === 0) {
    return null;
  }

  return (
    <section className="mb-6">
      <div className="flex items-center justify-between mb-3">
        <h2 className="text-lg font-semibold">Fremhevede meglere</h2>
        <span className="text-sm text-muted-foreground">{employees.length}</span>
      </div>
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {employees.map((employee) => (
          <Card key={employee.id} className="hover:shadow-md transition-shadow">
            <CardContent className="p-4">
              <div className="flex items-start gap-3">
                <Avatar className="h-12 w-12 shrink-0">
                  <AvatarImage src={resolveAvatarUrl(employee.profile_image_url, 96)} alt={employee.full_name} />
                  <AvatarFallback
                    className="text-white font-semibold"
                    style={{ backgroundColor: employee.office.color }}
                  >
                    {employee.initials}
                  </AvatarFallback>
                </Avatar>

                <div className="min-w-0 flex-1">
                  <h3 className="font-semibold truncate">
                    <Link href={`/employees/${employee.id}`} className="hover:text-primary">
                      {employee.full_name}
                    </Link>
                  </h3>
                  {employee.title && (
                    <p className="text-sm text-muted-foreground truncate">{employee.title}</p>
                  )}

                  {(employee.facebook_url ||
                    employee.instagram_url ||
                    employee.twitter_url ||
                    employee.linkedin_url) && (
                    <div className="flex items-center gap-3 mt-2">
                      {employee.facebook_url && (
                        <a
                          href={employee.facebook_url}
                          target="_blank"
                          rel="noopener noreferrer"
                          aria-label="Facebook"
                        >
                          <Facebook className="h-4 w-4 text-muted-foreground hover:text-primary" />
                        </a>
                      )}
                      {employee.instagram_url && (
                        <a
                          href={employee.instagram_url}
                          target="_blank"
                          rel="noopener noreferrer"
                          aria-label="Instagram"
                        >
                          <Instagram className="h-4 w-4 text-muted-foreground hover:text-primary" />
                        </a>
                      )}
                      {employee.twitter_url && (
                        <a
                          href={employee.twitter_url}
                          target="_blank"
                          rel="noopener noreferrer"
                          aria-label="Twitter"
                        >
                          <Twitter className="h-4 w-4 text-muted-foreground hover:text-primary" />
                        </a>
                      )}
                      {employee.linkedin_url && (
                        <a
                          href={employee.linkedin_url}
                          target="_blank"
                          rel="noopener noreferrer"
                          aria-label="LinkedIn"
                        >
                          <Linkedin className="h-4 w-4 text-muted-foreground hover:text-primary" />
                        </a>
                      )}
                    </div>
                  )}
                </div>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>
    </section>
  );
}
