"use client";

import { PortalFrame } from "./PortalFrame";

/**
 * BudPortalMockup Component
 * 
 * Interactive mockup of the Vitec Budportal (bidding portal) with Proaktiv branding.
 * Shows the bid form with consent options configured per Proaktiv requirements:
 * - Verdivurdering: ENABLED
 * - Newsletter: HIDDEN
 * - Financing: HIDDEN
 */

interface BudPortalMockupProps {
  /** Whether to show financing option (for Voss office demo) */
  showFinancing?: boolean;
}

export function BudPortalMockup({ showFinancing = false }: BudPortalMockupProps) {
  const mockupHtml = `
<div class="portal-container">
  <!-- Header -->
  <div class="portal-header bg-light">
    <div class="d-flex align-items-center justify-content-between">
      <div>
        <h4 class="mb-1" style="color: #272630; font-weight: 600;">Strandgata 15A</h4>
        <p class="text-muted mb-0" style="font-size: 14px;">5700 Voss</p>
      </div>
      <div style="width: 80px; height: 60px; background: #e9e7dc; border-radius: 4px; display: flex; align-items: center; justify-content: center;">
        <i class="fas fa-home" style="color: #bcab8a; font-size: 24px;"></i>
      </div>
    </div>
  </div>

  <!-- Progress Steps -->
  <div class="px-4 py-3 bg-white border-bottom">
    <div class="d-flex justify-content-between align-items-center" style="max-width: 400px; margin: 0 auto;">
      <div class="text-center">
        <div class="circle active" style="width: 36px; height: 36px; border-radius: 50%; border: 3px solid #272630; display: flex; align-items: center; justify-content: center; margin: 0 auto 4px;">
          <span style="font-weight: 600; color: #272630;">1</span>
        </div>
        <small style="font-size: 11px; color: #272630;">Fyll ut</small>
      </div>
      <div style="flex: 1; height: 2px; background: #ddd; margin: 0 10px;"></div>
      <div class="text-center">
        <div class="circle" style="width: 36px; height: 36px; border-radius: 50%; border: 3px solid #ddd; display: flex; align-items: center; justify-content: center; margin: 0 auto 4px;">
          <span style="font-weight: 600; color: #999;">2</span>
        </div>
        <small style="font-size: 11px; color: #999;">Signer</small>
      </div>
      <div style="flex: 1; height: 2px; background: #ddd; margin: 0 10px;"></div>
      <div class="text-center">
        <div class="circle" style="width: 36px; height: 36px; border-radius: 50%; border: 3px solid #ddd; display: flex; align-items: center; justify-content: center; margin: 0 auto 4px;">
          <span style="font-weight: 600; color: #999;">3</span>
        </div>
        <small style="font-size: 11px; color: #999;">Levert</small>
      </div>
    </div>
  </div>

  <!-- Form Content -->
  <div class="portal-content">
    <!-- Personal Info Section -->
    <h5 style="color: #272630; font-weight: 600; margin-bottom: 16px;">Dine opplysninger</h5>
    
    <div class="form-group">
      <label style="font-size: 14px; color: #666;">Fullt navn *</label>
      <input type="text" class="form-control" placeholder="Ola Nordmann" value="Ola Nordmann" style="border-color: #D6D4CD;">
    </div>

    <div class="row">
      <div class="col-6">
        <div class="form-group">
          <label style="font-size: 14px; color: #666;">Fødselsnummer *</label>
          <input type="text" class="form-control" placeholder="11 siffer" value="01019012345" style="border-color: #D6D4CD;">
        </div>
      </div>
      <div class="col-6">
        <div class="form-group">
          <label style="font-size: 14px; color: #666;">Telefon *</label>
          <input type="tel" class="form-control" placeholder="+47" value="+47 987 65 432" style="border-color: #D6D4CD;">
        </div>
      </div>
    </div>

    <div class="form-group">
      <label style="font-size: 14px; color: #666;">E-post *</label>
      <input type="email" class="form-control" placeholder="din@epost.no" value="ola@eksempel.no" style="border-color: #D6D4CD;">
    </div>

    <hr style="border-color: #e9e7dc; margin: 24px 0;">

    <!-- Bid Section -->
    <h5 style="color: #272630; font-weight: 600; margin-bottom: 16px;">Ditt bud</h5>
    
    <div class="form-group">
      <label style="font-size: 14px; color: #666;">Budsum *</label>
      <div class="input-group">
        <input type="text" class="form-control" placeholder="0" value="4 500 000" style="border-color: #D6D4CD; font-size: 18px; font-weight: 600;">
        <div class="input-group-append">
          <span class="input-group-text" style="background: #f8f9fa; border-color: #D6D4CD;">NOK</span>
        </div>
      </div>
    </div>

    <div class="form-group">
      <label style="font-size: 14px; color: #666;">Akseptfrist *</label>
      <input type="text" class="form-control" value="23.01.2026 kl. 12:00" style="border-color: #D6D4CD;">
    </div>

    <div class="form-group">
      <label style="font-size: 14px; color: #666;">Overtagelse</label>
      <input type="text" class="form-control" placeholder="Etter avtale" value="01.03.2026" style="border-color: #D6D4CD;">
    </div>

    <div class="form-group">
      <label style="font-size: 14px; color: #666;">Forbehold / betingelser</label>
      <textarea class="form-control" rows="2" placeholder="Eventuelle forbehold..." style="border-color: #D6D4CD;"></textarea>
    </div>

    <hr style="border-color: #e9e7dc; margin: 24px 0;">

    <!-- Consent Section -->
    <h5 style="color: #272630; font-weight: 600; margin-bottom: 16px;">Ønsker</h5>
    
    ${showFinancing ? `
    <div class="form-check mb-3">
      <input class="form-check-input" type="checkbox" id="consentFinancing">
      <label class="form-check-label" for="consentFinancing" style="font-size: 14px;">
        Finansiering
        <i class="far fa-question-circle text-muted ml-1" style="cursor: pointer;"></i>
      </label>
    </div>
    ` : ''}

    <div class="form-check mb-3">
      <input class="form-check-input" type="checkbox" id="consentFollowup" checked>
      <label class="form-check-label" for="consentFollowup" style="font-size: 14px;">
        Verdivurdering
        <i class="far fa-question-circle text-muted ml-1" style="cursor: pointer;"></i>
      </label>
      <small class="d-block text-muted mt-1">En av våre lokalkjente meglere kontakter deg for å avtale en tid for verdivurdering.</small>
    </div>

    <div class="form-check mb-3">
      <input class="form-check-input" type="checkbox" id="consentSearch">
      <label class="form-check-label" for="consentSearch" style="font-size: 14px;">
        Søkeprofil
        <i class="far fa-question-circle text-muted ml-1" style="cursor: pointer;"></i>
      </label>
    </div>

    <hr style="border-color: #e9e7dc; margin: 24px 0;">

    <!-- Privacy Link -->
    <p style="font-size: 13px; color: #666;">
      <a href="https://proaktiv.no/personvern" target="_blank" style="color: #272630;">
        <i class="far fa-question-circle mr-1"></i>
        Les om personvern
      </a>
    </p>

    <!-- Submit Button -->
    <button class="btn btn-primary btn-lg btn-block" style="background-color: #272630; border: none; font-weight: 600; padding: 14px;">
      Gå videre til signering
      <i class="fas fa-arrow-right ml-2"></i>
    </button>
  </div>

  <!-- Footer -->
  <div class="portal-footer text-center">
    <small style="color: #666;">
      Ved å sende inn dette skjemaet aksepterer du våre 
      <a href="#" style="color: #272630;">vilkår</a> og 
      <a href="https://proaktiv.no/personvern" style="color: #272630;">personvernerklæring</a>.
    </small>
  </div>
</div>

<!-- Cookie Banner -->
<div style="position: fixed; bottom: 0; left: 0; right: 0; background: #272630; color: white; padding: 12px 20px; font-size: 13px; display: flex; align-items: center; justify-content: space-between;">
  <span>Vi benytter informasjonskapsler for å sikre deg en god brukeropplevelse.</span>
  <div>
    <button class="btn btn-sm" style="background: #bcab8a; color: #272630; font-weight: 600; margin-right: 8px;">Innstillinger</button>
    <button class="btn btn-sm" style="background: white; color: #272630; font-weight: 600;">Godta alle</button>
  </div>
</div>
`;

  return (
    <PortalFrame
      content={mockupHtml}
      skinCssHref="/skins/proaktiv-bud.css"
      title="Budportal - Proaktiv"
      minHeight="900px"
    />
  );
}
