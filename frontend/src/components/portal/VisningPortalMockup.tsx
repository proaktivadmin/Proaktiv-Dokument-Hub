"use client";

import { PortalFrame } from "./PortalFrame";

/**
 * VisningPortalMockup Component
 * 
 * Interactive mockup of the Vitec Visningsportal (viewing registration portal) with Proaktiv branding.
 * Shows the registration form with consent options configured per Proaktiv requirements:
 * - Verdivurdering: ENABLED
 * - Budvarsel: ENABLED
 * - Newsletter: HIDDEN
 * - Financing: HIDDEN
 */

interface VisningPortalMockupProps {
  /** Whether to show financing option (for Voss office demo) */
  showFinancing?: boolean;
}

export function VisningPortalMockup({ showFinancing = false }: VisningPortalMockupProps) {
  const mockupHtml = `
<div class="portal-container">
  <!-- Header with Property Image -->
  <div style="height: 180px; background: linear-gradient(135deg, #272630 0%, #3E3D4A 100%); position: relative; overflow: hidden;">
    <div style="position: absolute; top: 20px; left: 20px; right: 20px;">
      <span style="background: #bcab8a; color: #272630; padding: 4px 12px; border-radius: 4px; font-size: 12px; font-weight: 600;">
        VISNING
      </span>
    </div>
    <div style="position: absolute; bottom: 20px; left: 20px; right: 20px; color: white;">
      <h4 style="margin: 0 0 4px 0; font-weight: 600;">Fjellveien 42</h4>
      <p style="margin: 0; opacity: 0.8; font-size: 14px;">5700 Voss</p>
    </div>
    <!-- Decorative corner accent -->
    <div style="position: absolute; top: 20px; right: 20px; width: 40px; height: 40px; border-top: 3px solid #D6D4CD; border-right: 3px solid #D6D4CD;"></div>
  </div>

  <!-- Viewing Info Banner -->
  <div style="background: #e9e7dc; padding: 16px 20px; border-bottom: 1px solid #D6D4CD;">
    <div class="d-flex align-items-center">
      <i class="far fa-calendar-alt mr-3" style="color: #272630; font-size: 20px;"></i>
      <div>
        <strong style="color: #272630;">Søndag 26. januar 2026</strong>
        <span class="text-muted ml-2">kl. 12:00 - 13:00</span>
      </div>
    </div>
  </div>

  <!-- Form Content -->
  <div class="portal-content">
    <h5 style="color: #272630; font-weight: 600; margin-bottom: 16px;">Meld deg på visning</h5>
    
    <!-- Contact Info -->
    <div class="form-group">
      <label style="font-size: 14px; color: #666;">Fullt navn *</label>
      <input type="text" class="form-control" placeholder="Ditt navn" value="Kari Nordmann" style="border-color: #D6D4CD;">
    </div>

    <div class="row">
      <div class="col-6">
        <div class="form-group">
          <label style="font-size: 14px; color: #666;">Telefon *</label>
          <input type="tel" class="form-control" placeholder="+47" value="+47 912 34 567" style="border-color: #D6D4CD;">
        </div>
      </div>
      <div class="col-6">
        <div class="form-group">
          <label style="font-size: 14px; color: #666;">Antall personer *</label>
          <select class="form-control" style="border-color: #D6D4CD;">
            <option>1 person</option>
            <option selected>2 personer</option>
            <option>3 personer</option>
            <option>4+ personer</option>
          </select>
        </div>
      </div>
    </div>

    <div class="form-group">
      <label style="font-size: 14px; color: #666;">E-post *</label>
      <input type="email" class="form-control" placeholder="din@epost.no" value="kari@eksempel.no" style="border-color: #D6D4CD;">
    </div>

    <hr style="border-color: #e9e7dc; margin: 24px 0;">

    <!-- Consent Section -->
    <p style="font-size: 14px; color: #666; margin-bottom: 16px;">
      Hvis du ønsker videre oppfølging på eiendommen trenger vi mer informasjon:
    </p>
    
    ${showFinancing ? `
    <div class="form-check mb-3">
      <input class="form-check-input" type="checkbox" id="consentFinancing">
      <label class="form-check-label" for="consentFinancing" style="font-size: 14px;">
        Jeg ønsker tilbud om finansiering
        <i class="far fa-question-circle text-muted ml-1" style="cursor: pointer;"></i>
      </label>
      <small class="d-block text-muted mt-1">Din kontaktinformasjon sendes til en bankrådgiver.</small>
    </div>
    ` : ''}

    <div class="form-check mb-3">
      <input class="form-check-input" type="checkbox" id="consentFollowup" checked>
      <label class="form-check-label" for="consentFollowup" style="font-size: 14px;">
        Jeg ønsker verdivurdering av min bolig
        <i class="far fa-question-circle text-muted ml-1" style="cursor: pointer;"></i>
      </label>
      <small class="d-block text-muted mt-1">En eiendomsmegler vil kontakte deg og avtale tid for verdivurdering.</small>
    </div>

    <div class="form-check mb-3">
      <input class="form-check-input" type="checkbox" id="consentBidInfo" checked>
      <label class="form-check-label" for="consentBidInfo" style="font-size: 14px;">
        Jeg ønsker bli informert om bud på eiendommen
        <i class="far fa-question-circle text-muted ml-1" style="cursor: pointer;"></i>
      </label>
      <small class="d-block text-muted mt-1">Du vil bli registrert som interessent og varslet om bud frem til eiendommen er solgt.</small>
    </div>

    <hr style="border-color: #e9e7dc; margin: 24px 0;">

    <!-- Sales Document -->
    <div class="form-check mb-4">
      <input class="form-check-input" type="checkbox" id="getSalesDoc" checked>
      <label class="form-check-label" for="getSalesDoc" style="font-size: 14px;">
        Send meg salgsoppgaven på e-post
      </label>
    </div>

    <!-- Privacy Link -->
    <p style="font-size: 13px; margin-bottom: 20px;">
      <a href="https://proaktiv.no/personvern" target="_blank" style="color: #272630;">
        <span class="link-text">Les om personvern</span>
        <i class="far fa-question-circle ml-1"></i>
      </a>
    </p>

    <!-- Submit Button -->
    <button class="btn btn-primary btn-lg btn-block" style="background-color: #272630; border: none; font-weight: 600; padding: 14px;">
      Meld meg på visning
      <i class="fas fa-check ml-2"></i>
    </button>
  </div>

  <!-- Broker Info -->
  <div style="background: #f8f9fa; padding: 20px; border-top: 1px solid #eee;">
    <div class="d-flex align-items-center">
      <div style="width: 50px; height: 50px; background: #e9e7dc; border-radius: 50%; display: flex; align-items: center; justify-content: center; margin-right: 15px;">
        <i class="fas fa-user" style="color: #bcab8a; font-size: 20px;"></i>
      </div>
      <div>
        <strong style="color: #272630;">Per Hansen</strong>
        <p style="margin: 0; font-size: 13px; color: #666;">Eiendomsmegler MNEF</p>
        <p style="margin: 0; font-size: 13px; color: #666;">Tlf: 56 52 00 00</p>
      </div>
    </div>
  </div>

  <!-- Footer -->
  <div class="portal-footer text-center">
    <img src="/assets/proaktiv-logo-black.png" alt="Proaktiv" style="height: 24px; opacity: 0.6;" onerror="this.style.display='none'">
  </div>
</div>

<!-- Cookie Banner -->
<div style="position: fixed; bottom: 0; left: 0; right: 0; background: #272630; color: white; padding: 12px 20px; font-size: 13px; display: flex; align-items: center; justify-content: space-between;">
  <span>Vi benytter informasjonskapsler for funksjonalitet i visningsportalen.</span>
  <button class="btn btn-sm" style="background: white; color: #272630; font-weight: 600;">Godta</button>
</div>
`;

  return (
    <PortalFrame
      content={mockupHtml}
      skinCssHref="/skins/proaktiv-visning.css"
      title="Visningsportal - Proaktiv"
      minHeight="850px"
    />
  );
}
