/**
 * Vitec Test Scenarios
 *
 * Standardized testdata presets to mimic different property types / situations
 * in Vitec Next preview (so vitec-if / vitec-foreach branches behave predictably).
 */

export interface VitecTestScenario {
  id: string;
  label: string;
  description: string;
  model_overrides: {
    eiendom?: {
      eieform?: string;
      boligtype?: string;
    };
    kjopere_count?: number;
    selgere_count?: number;
  };
  value_overrides: Record<string, string>;
}

export const VITEC_TEST_SCENARIOS: VitecTestScenario[] = [
  {
    id: "eierseksjon",
    label: "Eierseksjon",
    description: "Eierseksjon/selveier (typisk leilighet).",
    model_overrides: {
      eiendom: { eieform: "Selveier", boligtype: "Eierseksjon" },
      kjopere_count: 1,
      selgere_count: 1,
    },
    value_overrides: {
      "eiendom.boligtype": "Selveierleilighet",
      "eiendom.eieform": "Selveier",
    },
  },
  {
    id: "enebolig",
    label: "Enebolig",
    description: "Enebolig/selveier.",
    model_overrides: {
      eiendom: { eieform: "Selveier", boligtype: "Enebolig" },
      kjopere_count: 1,
      selgere_count: 1,
    },
    value_overrides: {
      "eiendom.boligtype": "Enebolig",
      "eiendom.eieform": "Selveier",
    },
  },
  {
    id: "andel",
    label: "Andel (borettslag)",
    description: "Andelsleilighet i borettslag (forkjøpsrett/styregodkjenning kan trigge).",
    model_overrides: {
      eiendom: { eieform: "Andel", boligtype: "Andelsleilighet" },
      kjopere_count: 1,
      selgere_count: 1,
    },
    value_overrides: {
      "eiendom.boligtype": "Andelsleilighet",
      "eiendom.eieform": "Andel",
    },
  },
  {
    id: "flere_kjopere",
    label: "Flere kjøpere",
    description: "Scenario med 2 kjøpere (Model.kjopere.Count > 1).",
    model_overrides: {
      kjopere_count: 2,
      selgere_count: 1,
    },
    value_overrides: {},
  },
];

export function getScenarioById(id: string): VitecTestScenario | undefined {
  return VITEC_TEST_SCENARIOS.find((s) => s.id === id);
}

