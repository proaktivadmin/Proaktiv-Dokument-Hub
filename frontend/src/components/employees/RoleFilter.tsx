"use client"

import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { X } from "lucide-react"

const VITEC_ROLES = [
    { value: "eiendomsmegler", label: "Eiendomsmegler" },
    { value: "eiendomsmeglerfullmektig", label: "Eiendomsmeglerfullmektig" },
    { value: "daglig leder", label: "Daglig leder" },
    { value: "superbruker", label: "Superbruker" },
    { value: "oppgjør", label: "Oppgjør" },
]

interface RoleFilterProps {
    selectedRole: string | null
    onRoleChange: (role: string | null) => void
}

export function RoleFilter({ selectedRole, onRoleChange }: RoleFilterProps) {
    return (
        <Card>
            <CardHeader>
                <div className="flex items-center justify-between">
                    <CardTitle className="text-sm font-medium">Systemrolle</CardTitle>
                    {selectedRole && (
                        <Button
                            variant="ghost"
                            size="sm"
                            onClick={() => onRoleChange(null)}
                            className="h-6 px-2"
                        >
                            <X className="h-3 w-3" />
                        </Button>
                    )}
                </div>
            </CardHeader>
            <CardContent className="space-y-2">
                {VITEC_ROLES.map((role) => {
                    const isSelected = selectedRole === role.value
                    return (
                        <button
                            key={role.value}
                            onClick={() => onRoleChange(isSelected ? null : role.value)}
                            className={`w-full text-left px-3 py-2 rounded-md text-sm transition-colors ${isSelected
                                    ? "bg-primary text-primary-foreground"
                                    : "hover:bg-muted"
                                }`}
                        >
                            {role.label}
                        </button>
                    )
                })}
            </CardContent>
        </Card>
    )
}
