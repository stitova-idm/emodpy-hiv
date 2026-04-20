import emod_api.schema_to_class as s2c
from emodpy.campaign.individual_intervention import IndividualIntervention
from emodpy.utils import validate_value_range
from emodpy.campaign.utils import set_event
from emodpy_hiv.utils.emod_enum import StrEnum, EventOrConfig
from emodpy_hiv.campaign.common import CommonInterventionParameters
from emodpy_hiv.campaign.waning_config import AbstractWaningConfig
from emodpy_hiv.utils.distributions import BaseDistribution
from emod_api import campaign as api_campaign

from typing import Union


class CreateNucleotideSequenceFrom(StrEnum):
    BARCODE_STRING = 'BARCODE_STRING'
    NUCLEOTIDE_SEQUENCE = 'NUCLEOTIDE_SEQUENCE'
    ALLELE_FREQUENCIES = 'ALLELE_FREQUENCIES'


class NonAdherenceOption(StrEnum):
    NEXT_UPDATE = 'NEXT_UPDATE'
    NEXT_DOSAGE_TIME = 'NEXT_DOSAGE_TIME'
    LOST_TAKE_NEXT = 'LOST_TAKE_NEXT'
    STOP = 'STOP'


class MalariaDiagnosticType(StrEnum):
    BLOOD_SMEAR_PARASITES = 'BLOOD_SMEAR_PARASITES'
    BLOOD_SMEAR_GAMETOCYTES = 'BLOOD_SMEAR_GAMETOCYTES'
    PCR_PARASITES = 'PCR_PARASITES'
    PCR_GAMETOCYTES = 'PCR_GAMETOCYTES'
    PF_HRP2 = 'PF_HRP2'
    TRUE_PARASITE_DENSITY = 'TRUE_PARASITE_DENSITY'
    FEVER = 'FEVER'


class MalariaChallengeType(StrEnum):
    INFECTIOUS_BITES = 'InfectiousBites'
    SPOROZOITES = 'Sporozoites'


class AntimalarialDrug(IndividualIntervention):
    """
    The **AntimalarialDrug** intervention class distributes an antimalarial drug to an individual. The drug type
    must be defined in the configuration parameter **Malaria_Drug_Params**.

    Args:
        campaign (api_campaign, required):
            An instance of the emod_api.campaign module.

        drug_type (str, required):
            The type of drug to distribute. This must match a value defined in the configuration parameter
            **Malaria_Drug_Params[X].Name**.

        common_intervention_parameters (CommonInterventionParameters, optional):
            The CommonInterventionParameters object that contains the 5 common
            parameters: cost, intervention_name, new_property_value, disqualifying_properties, dont_allow_duplicates.
            Default value: None
    """

    def __init__(self,
                 campaign: api_campaign,
                 drug_type: str,
                 common_intervention_parameters: CommonInterventionParameters = None):
        super().__init__(campaign, 'AntimalarialDrug', common_intervention_parameters)

        if not drug_type:
            raise ValueError("'drug_type' must be a non-empty string.")
        self._intervention.Drug_Type = drug_type


class MalariaDiagnostic(IndividualIntervention):
    """
    The **MalariaDiagnostic** intervention class runs a malaria diagnostic test on an individual and
    broadcasts events or distributes interventions based on the result.

    User can either set the diagnosis config parameters:
    - `positive_diagnosis_config` (required)
    - `negative_diagnosis_config` (optional)

    or set the diagnosis event parameters:
    - `positive_diagnosis_event` (required)
    - `negative_diagnosis_event` (optional)

    but not both.

    Args:
        campaign (api_campaign, required):
            An instance of the emod_api.campaign module.

        diagnostic_type (MalariaDiagnosticType, optional):
            The type of malaria diagnostic used. Possible values are:
            * BLOOD_SMEAR_PARASITES
            * BLOOD_SMEAR_GAMETOCYTES
            * PCR_PARASITES
            * PCR_GAMETOCYTES
            * PF_HRP2
            * TRUE_PARASITE_DENSITY
            * FEVER
            Default value: MalariaDiagnosticType.BLOOD_SMEAR_PARASITES

        detection_threshold (float, optional):
            The diagnostic detection threshold for parasites, in units of microliters of blood.
            Minimum value: 0
            Maximum value: 1000000
            Default value: 0

        measurement_sensitivity (float, optional):
            The number of microliters of blood tested to find single parasites/gametocytes in a
            traditional smear.
            Minimum value: 0
            Maximum value: 1000000
            Default value: 0.1

        days_to_diagnosis (float, optional):
            The number of days from diagnosis (which is done when the intervention is distributed) until a
            positive response is performed. The response to a negative diagnosis is done immediately when the
            diagnosis is made.
            Minimum value: 0
            Maximum value: 3.40282e+38
            Default value: 0

        treatment_fraction (float, optional):
            The fraction of positive diagnoses that are treated (receive Positive_Diagnosis_Config or
            Positive_Diagnosis_Event).
            Minimum value: 0
            Maximum value: 1
            Default value: 1

        positive_diagnosis_config (IndividualIntervention, optional):
            The intervention distributed to individuals who test positive. Only used when
            Event_Or_Config is set to Config.
            Default value: None

        negative_diagnosis_config (IndividualIntervention, optional):
            The intervention distributed to individuals who test negative. Only used when
            Event_Or_Config is set to Config.
            Default value: None

        positive_diagnosis_event (str, optional):
            If the test is positive, this event will be broadcast. Only used when Event_Or_Config is
            set to Event. See the EMOD documentation for valid built-in events or use your own custom event.
            Default value: None

        negative_diagnosis_event (str, optional):
            If the test is negative, this event will be broadcast. Only used when Event_Or_Config is
            set to Event. See the EMOD documentation for valid built-in events or use your own custom event.
            Default value: None

        common_intervention_parameters (CommonInterventionParameters, optional):
            The CommonInterventionParameters object that contains the 5 common
            parameters: cost, intervention_name, new_property_value, disqualifying_properties, dont_allow_duplicates.
            Default value: None
    """

    def __init__(self,
                 campaign: api_campaign,
                 diagnostic_type: MalariaDiagnosticType = MalariaDiagnosticType.BLOOD_SMEAR_PARASITES,
                 detection_threshold: float = 0,
                 measurement_sensitivity: float = 0.1,
                 days_to_diagnosis: float = 0,
                 treatment_fraction: float = 1,
                 positive_diagnosis_config: IndividualIntervention = None,
                 negative_diagnosis_config: IndividualIntervention = None,
                 positive_diagnosis_event: str = None,
                 negative_diagnosis_event: str = None,
                 common_intervention_parameters: CommonInterventionParameters = None):
        super().__init__(campaign, 'MalariaDiagnostic', common_intervention_parameters)

        if any([positive_diagnosis_config, negative_diagnosis_config]) and any([positive_diagnosis_event, negative_diagnosis_event]):
            raise ValueError('You can only set either diagnosis_config(s) or diagnosis_event(s), but not both.')
        if not any([positive_diagnosis_config, negative_diagnosis_config, positive_diagnosis_event, negative_diagnosis_event]):
            raise ValueError('You must set either diagnosis_config(s) or diagnosis_event(s).')

        self._intervention.Diagnostic_Type = diagnostic_type
        self._intervention.Detection_Threshold = validate_value_range(detection_threshold, 'detection_threshold', 0, 1e6, float)
        self._intervention.Measurement_Sensitivity = validate_value_range(measurement_sensitivity, 'measurement_sensitivity', 0, 1e6, float)
        self._intervention.Days_To_Diagnosis = validate_value_range(days_to_diagnosis, 'days_to_diagnosis', 0, 3.40282e+38, float)
        self._intervention.Treatment_Fraction = validate_value_range(treatment_fraction, 'treatment_fraction', 0, 1, float)

        if positive_diagnosis_config or negative_diagnosis_config:
            if not positive_diagnosis_config:
                raise ValueError('positive_diagnosis_config must be set if you set negative_diagnosis_config.')
            self._intervention.Positive_Diagnosis_Config = positive_diagnosis_config.to_schema_dict()
            if negative_diagnosis_config:
                self._intervention.Negative_Diagnosis_Config = negative_diagnosis_config.to_schema_dict()
            self._intervention.Event_Or_Config = EventOrConfig.Config
            self._intervention.pop("Positive_Diagnosis_Event")
            self._intervention.pop("Negative_Diagnosis_Event")
        else:
            if not positive_diagnosis_event:
                raise ValueError('positive_diagnosis_event must be set if you set negative_diagnosis_event.')
            self._intervention.Positive_Diagnosis_Event = set_event(positive_diagnosis_event, 'positive_diagnosis_event', campaign, False)
            self._intervention.Negative_Diagnosis_Event = set_event(negative_diagnosis_event, 'negative_diagnosis_event', campaign, True)
            self._intervention.Event_Or_Config = EventOrConfig.Event
            self._intervention.pop("Positive_Diagnosis_Config")
            self._intervention.pop("Negative_Diagnosis_Config")


class MalariaChallenge(IndividualIntervention):
    """
    The **MalariaChallenge** intervention class infects individuals with malaria either via infectious
    bites or direct sporozoite injection, for use in challenge studies.

    Args:
        campaign (api_campaign, required):
            An instance of the emod_api.campaign module.

        challenge_type (MalariaChallengeType, optional):
            The type of malaria challenge. Use **MalariaChallengeType.INFECTIOUS_BITES** with
            **infectious_bite_count** or **MalariaChallengeType.SPOROZOITES** with **sporozoite_count**.
            Default value: MalariaChallengeType.INFECTIOUS_BITES

        coverage (float, optional):
            The fraction of individuals receiving the intervention.
            Minimum value: 0
            Maximum value: 1
            Default value: 1

        infectious_bite_count (int, optional):
            The number of infectious bites per person. Used when challenge_type is
            **MalariaChallengeType.INFECTIOUS_BITES**.
            Minimum value: 0
            Maximum value: 1000
            Default value: 1

        sporozoite_count (int, optional):
            The number of sporozoites per person. Used when challenge_type is
            **MalariaChallengeType.SPOROZOITES**.
            Minimum value: 0
            Maximum value: 1000
            Default value: 1

        common_intervention_parameters (CommonInterventionParameters, optional):
            The CommonInterventionParameters object that contains the 5 common
            parameters: cost, intervention_name, new_property_value, disqualifying_properties, dont_allow_duplicates.
            Default value: None
    """

    def __init__(self,
                 campaign: api_campaign,
                 challenge_type: MalariaChallengeType = MalariaChallengeType.INFECTIOUS_BITES,
                 coverage: float = 1,
                 infectious_bite_count: int = 1,
                 sporozoite_count: int = 1,
                 common_intervention_parameters: CommonInterventionParameters = None):
        super().__init__(campaign, 'MalariaChallenge', common_intervention_parameters)

        self._intervention.Challenge_Type = challenge_type
        self._intervention.Coverage = validate_value_range(coverage, 'coverage', 0, 1, float)
        self._intervention.Infectious_Bite_Count = validate_value_range(infectious_bite_count, 'infectious_bite_count', 0, 1000, int)
        self._intervention.Sporozoite_Count = validate_value_range(sporozoite_count, 'sporozoite_count', 0, 1000, int)


class RTSSVaccine(IndividualIntervention):
    """
    The **RTSSVaccine** intervention class distributes the RTS,S malaria vaccine to an individual,
    boosting their antibody concentration to protect against infection.

    Args:
        campaign (api_campaign, required):
            An instance of the emod_api.campaign module.

        boosted_antibody_concentration (float, optional):
            The boosted antibody concentration, where unity equals the maximum from natural exposure.
            Minimum value: 0
            Maximum value: 3.40282e+38
            Default value: 1

        common_intervention_parameters (CommonInterventionParameters, optional):
            The CommonInterventionParameters object that contains the 5 common
            parameters: cost, intervention_name, new_property_value, disqualifying_properties, dont_allow_duplicates.
            Default value: None
    """

    def __init__(self,
                 campaign: api_campaign,
                 boosted_antibody_concentration: float = 1,
                 common_intervention_parameters: CommonInterventionParameters = None):
        super().__init__(campaign, 'RTSSVaccine', common_intervention_parameters)

        self._intervention.Boosted_Antibody_Concentration = validate_value_range(boosted_antibody_concentration, 'boosted_antibody_concentration', 0, 3.40282e+38, float)


class SimpleBednet(IndividualIntervention):
    """
    The **SimpleBednet** intervention class distributes an insecticide-treated bed net (ITN) to an individual.
    The net has configurable repelling, blocking, killing, and usage effects that can each wane over time.

    Args:
        campaign (api_campaign, required):
            An instance of the emod_api.campaign module.

        blocking_config (AbstractWaningConfig, required):
            Configures the rate of blocking for indoor mosquito feeds on individuals with an ITN,
            conditional on the mosquito NOT being repelled. Specify how this effect decays over time
            using one of the Waning Config classes in emodpy_hiv.campaign.waning_config.

        killing_config (AbstractWaningConfig, required):
            The configuration of killing efficacy and waning for the ITN, conditional on a successfully
            blocked feed (only blocked vectors can be killed). Specify how this effect decays over time
            using one of the Waning Config classes in emodpy_hiv.campaign.waning_config.

        repelling_config (AbstractWaningConfig, required):
            The configuration of repelling efficacy of the intervention. A vector is repelled before any
            blocking or killing can occur. Specify how this effect decays over time using one of the
            Waning Config classes in emodpy_hiv.campaign.waning_config.

        usage_config (AbstractWaningConfig, required):
            The WaningEffect used to determine when and if an individual is using a bed net. Specify how
            this effect decays over time using one of the Waning Config classes in
            emodpy_hiv.campaign.waning_config.

        insecticide_name (str, optional):
            The name of the insecticide defined in the configuration parameter **Insecticides** for this
            intervention. If insecticides are not being used, this can be left empty.
            Default value: None

        common_intervention_parameters (CommonInterventionParameters, optional):
            The CommonInterventionParameters object that contains the 5 common
            parameters: cost, intervention_name, new_property_value, disqualifying_properties, dont_allow_duplicates.
            Default value: None
    """

    def __init__(self,
                 campaign: api_campaign,
                 blocking_config: AbstractWaningConfig,
                 killing_config: AbstractWaningConfig,
                 repelling_config: AbstractWaningConfig,
                 usage_config: AbstractWaningConfig,
                 insecticide_name: str = None,
                 common_intervention_parameters: CommonInterventionParameters = None):
        super().__init__(campaign, 'SimpleBednet', common_intervention_parameters)

        for param_name, waning in [('blocking_config', blocking_config),
                                   ('killing_config', killing_config),
                                   ('repelling_config', repelling_config),
                                   ('usage_config', usage_config)]:
            if not isinstance(waning, AbstractWaningConfig):
                raise ValueError(f"'{param_name}' must be an instance of AbstractWaningConfig, not {type(waning)}.")

        self._intervention.Blocking_Config = blocking_config.to_schema_dict(campaign)
        self._intervention.Killing_Config = killing_config.to_schema_dict(campaign)
        self._intervention.Repelling_Config = repelling_config.to_schema_dict(campaign)
        self._intervention.Usage_Config = usage_config.to_schema_dict(campaign)

        if insecticide_name is not None:
            self._intervention.Insecticide_Name = insecticide_name


class UsageDependentBednet(IndividualIntervention):
    """
    The **UsageDependentBednet** intervention class distributes a bed net to an individual whose usage
    varies over time based on a list of waning effects. The net expires after a duration drawn from a
    configurable distribution and can broadcast events when received, used, or discarded.

    Args:
        campaign (api_campaign, required):
            An instance of the emod_api.campaign module.

        blocking_config (AbstractWaningConfig, required):
            Configures the rate of blocking for indoor mosquito feeds on individuals with an ITN,
            conditional on the mosquito NOT being repelled. Specify how this effect decays over time
            using one of the Waning Config classes in emodpy_hiv.campaign.waning_config.

        killing_config (AbstractWaningConfig, required):
            The configuration of killing efficacy and waning for the ITN, conditional on a successfully
            blocked feed (only blocked vectors can be killed). Specify how this effect decays over time
            using one of the Waning Config classes in emodpy_hiv.campaign.waning_config.

        repelling_config (AbstractWaningConfig, required):
            The configuration of repelling efficacy of the intervention. A vector is repelled before any
            blocking or killing can occur. Specify how this effect decays over time using one of the
            Waning Config classes in emodpy_hiv.campaign.waning_config.

        usage_config_list (list[AbstractWaningConfig], required):
            A list of WaningEffects whose effects are multiplied together to determine the overall usage
            effect. Use one of the Waning Config classes from emodpy_hiv.campaign.waning_config.

        expiration_period_distribution (BaseDistribution, required):
            A distribution determining how long the bed net lasts before expiring. Use one of the
            following distribution classes from emodpy_hiv.utils.distributions:
            * ConstantDistribution
            * UniformDistribution
            * GaussianDistribution
            * ExponentialDistribution
            * PoissonDistribution
            * LogNormalDistribution
            * DualConstantDistribution
            * WeibullDistribution
            * DualExponentialDistribution

        insecticide_name (str, optional):
            The name of the insecticide defined in the configuration parameter **Insecticides** for this
            intervention. If insecticides are not being used, this can be left empty.
            Default value: None

        received_event (str, optional):
            The event broadcast when a new net is received (either the first net or a replacement net).
            Default value: None

        using_event (str, optional):
            The event broadcast each time step in which a bed net is being used.
            Default value: None

        discard_event (str, optional):
            The event broadcast when an individual discards their bed net, either by replacing it or
            due to the expiration timer.
            Default value: None

        common_intervention_parameters (CommonInterventionParameters, optional):
            The CommonInterventionParameters object that contains the 5 common
            parameters: cost, intervention_name, new_property_value, disqualifying_properties, dont_allow_duplicates.
            Default value: None
    """

    def __init__(self,
                 campaign: api_campaign,
                 blocking_config: AbstractWaningConfig,
                 killing_config: AbstractWaningConfig,
                 repelling_config: AbstractWaningConfig,
                 usage_config_list: list,
                 expiration_period_distribution: BaseDistribution,
                 insecticide_name: str = None,
                 received_event: str = None,
                 using_event: str = None,
                 discard_event: str = None,
                 common_intervention_parameters: CommonInterventionParameters = None):
        super().__init__(campaign, 'UsageDependentBednet', common_intervention_parameters)

        for param_name, waning in [('blocking_config', blocking_config),
                                   ('killing_config', killing_config),
                                   ('repelling_config', repelling_config)]:
            if not isinstance(waning, AbstractWaningConfig):
                raise ValueError(f"'{param_name}' must be an instance of AbstractWaningConfig, not {type(waning)}.")

        if not usage_config_list:
            raise ValueError("'usage_config_list' must be a non-empty list of AbstractWaningConfig instances.")
        for i, waning in enumerate(usage_config_list):
            if not isinstance(waning, AbstractWaningConfig):
                raise ValueError(f"'usage_config_list[{i}]' must be an instance of AbstractWaningConfig, not {type(waning)}.")

        if not isinstance(expiration_period_distribution, BaseDistribution):
            raise ValueError(f"expiration_period_distribution must be an instance of BaseDistribution, not {type(expiration_period_distribution)}.")

        self._intervention.Blocking_Config = blocking_config.to_schema_dict(campaign)
        self._intervention.Killing_Config = killing_config.to_schema_dict(campaign)
        self._intervention.Repelling_Config = repelling_config.to_schema_dict(campaign)
        self._intervention.Usage_Config_List = [w.to_schema_dict(campaign) for w in usage_config_list]

        self.set_distribution(expiration_period_distribution, 'Expiration_Period')

        if insecticide_name is not None:
            self._intervention.Insecticide_Name = insecticide_name

        self._intervention.Received_Event = set_event(received_event, 'received_event', campaign, True)
        self._intervention.Using_Event = set_event(using_event, 'using_event', campaign, True)
        self._intervention.Discard_Event = set_event(discard_event, 'discard_event', campaign, True)


class IRSHousingModification(IndividualIntervention):
    """
    The **IRSHousingModification** intervention class applies indoor residual spraying (IRS) to an individual's
    housing. Vectors entering the dwelling may be repelled or killed based on configurable waning effects.

    Args:
        campaign (api_campaign, required):
            An instance of the emod_api.campaign module.

        killing_config (AbstractWaningConfig, required):
            The configuration of killing efficacy and waning for the housing modification. Killing is
            conditional on the vector not being repelled before feeding. Specify how this effect decays
            over time using one of the Waning Config classes in emodpy_hiv.campaign.waning_config.

        repelling_config (AbstractWaningConfig, required):
            The configuration of repelling efficacy of the intervention. A vector is repelled before any
            blocking or killing can occur. Specify how this effect decays over time using one of the
            Waning Config classes in emodpy_hiv.campaign.waning_config.

        insecticide_name (str, optional):
            The name of the insecticide defined in the configuration parameter **Insecticides** for this
            intervention. If insecticides are not being used, this can be left empty.
            Default value: None

        common_intervention_parameters (CommonInterventionParameters, optional):
            The CommonInterventionParameters object that contains the 5 common
            parameters: cost, intervention_name, new_property_value, disqualifying_properties, dont_allow_duplicates.
            Default value: None
    """

    def __init__(self,
                 campaign: api_campaign,
                 killing_config: AbstractWaningConfig,
                 repelling_config: AbstractWaningConfig,
                 insecticide_name: str = None,
                 common_intervention_parameters: CommonInterventionParameters = None):
        super().__init__(campaign, 'IRSHousingModification', common_intervention_parameters)

        for param_name, waning in [('killing_config', killing_config),
                                   ('repelling_config', repelling_config)]:
            if not isinstance(waning, AbstractWaningConfig):
                raise ValueError(f"'{param_name}' must be an instance of AbstractWaningConfig, not {type(waning)}.")

        self._intervention.Killing_Config = killing_config.to_schema_dict(campaign)
        self._intervention.Repelling_Config = repelling_config.to_schema_dict(campaign)

        if insecticide_name is not None:
            self._intervention.Insecticide_Name = insecticide_name


class InsecticideWaningEffectRBK:
    """
    Defines per-insecticide repelling, blocking, and killing waning effects for use in
    **MultiInsecticideUsageDependentBednet**. Each element in the **Insecticides** array of that
    intervention is an instance of this class.

    Args:
        insecticide_name (str, required):
            The name of the insecticide defined in the configuration parameter **Insecticides**.

        repelling_config (AbstractWaningConfig, required):
            The configuration of repelling efficacy and waning for this insecticide.

        blocking_config (AbstractWaningConfig, required):
            The configuration of blocking efficacy and waning for this insecticide.

        killing_config (AbstractWaningConfig, required):
            The configuration of killing efficacy and waning for this insecticide.
    """

    def __init__(self,
                 insecticide_name: str,
                 repelling_config: AbstractWaningConfig,
                 blocking_config: AbstractWaningConfig,
                 killing_config: AbstractWaningConfig):
        if not insecticide_name:
            raise ValueError("'insecticide_name' must be a non-empty string.")
        for param_name, waning in [('repelling_config', repelling_config),
                                   ('blocking_config', blocking_config),
                                   ('killing_config', killing_config)]:
            if not isinstance(waning, AbstractWaningConfig):
                raise ValueError(f"'{param_name}' must be an instance of AbstractWaningConfig, not {type(waning)}.")
        self.insecticide_name = insecticide_name
        self.repelling_config = repelling_config
        self.blocking_config = blocking_config
        self.killing_config = killing_config

    def to_schema_dict(self, campaign) -> s2c.ReadOnlyDict:
        iew = s2c.get_class_with_defaults("idmType:InsecticideWaningEffect_RBK", schema_json=campaign.get_schema())
        iew.Insecticide_Name = self.insecticide_name
        iew.Repelling_Config = self.repelling_config.to_schema_dict(campaign)
        iew.Blocking_Config = self.blocking_config.to_schema_dict(campaign)
        iew.Killing_Config = self.killing_config.to_schema_dict(campaign)
        iew.finalize()
        return iew


class InsecticideWaningEffectRK:
    """
    Defines per-insecticide repelling and killing waning effects for use in
    **MultiInsecticideIRSHousingModification**. Each element in the **Insecticides** array of that
    intervention is an instance of this class.

    Args:
        insecticide_name (str, required):
            The name of the insecticide defined in the configuration parameter **Insecticides**.

        repelling_config (AbstractWaningConfig, required):
            The configuration of repelling efficacy and waning for this insecticide.

        killing_config (AbstractWaningConfig, required):
            The configuration of killing efficacy and waning for this insecticide.
    """

    def __init__(self,
                 insecticide_name: str,
                 repelling_config: AbstractWaningConfig,
                 killing_config: AbstractWaningConfig):
        if not insecticide_name:
            raise ValueError("'insecticide_name' must be a non-empty string.")
        for param_name, waning in [('repelling_config', repelling_config),
                                   ('killing_config', killing_config)]:
            if not isinstance(waning, AbstractWaningConfig):
                raise ValueError(f"'{param_name}' must be an instance of AbstractWaningConfig, not {type(waning)}.")
        self.insecticide_name = insecticide_name
        self.repelling_config = repelling_config
        self.killing_config = killing_config

    def to_schema_dict(self, campaign) -> s2c.ReadOnlyDict:
        iew = s2c.get_class_with_defaults("idmType:InsecticideWaningEffect_RK", schema_json=campaign.get_schema())
        iew.Insecticide_Name = self.insecticide_name
        iew.Repelling_Config = self.repelling_config.to_schema_dict(campaign)
        iew.Killing_Config = self.killing_config.to_schema_dict(campaign)
        iew.finalize()
        return iew


class AdherentDrug(IndividualIntervention):
    """
    The **AdherentDrug** intervention class distributes a multi-dose antimalarial drug regimen where
    adherence to each dose is controlled by a waning effect. Non-adherence behavior is configurable
    per dose.

    Args:
        campaign (api_campaign, required):
            An instance of the emod_api.campaign module.

        adherence_config (AbstractWaningConfig, required):
            Configuration for the probability of taking each dose of the drug. Use a waning effect
            class to specify how this probability changes over time.

        doses (list[list[str]], required):
            Two-dimensional array of drug names from **Malaria_Drug_Params**. Each inner list defines
            the set of drugs administered in a single dose.

        non_adherence_options (list[NonAdherenceOption], required):
            List of actions taken if a dose is not taken. Possible values per element:
            * NonAdherenceOption.NEXT_UPDATE
            * NonAdherenceOption.NEXT_DOSAGE_TIME
            * NonAdherenceOption.LOST_TAKE_NEXT
            * NonAdherenceOption.STOP

        non_adherence_distribution (list[float], required):
            Probability values assigned to the corresponding options in **non_adherence_options**.
            Must sum to 1.

        dose_interval (float, optional):
            The number of days to wait between doses.
            Minimum value: 0
            Maximum value: 100000
            Default value: 1

        max_dose_consideration_duration (float, optional):
            Maximum number of days an individual will consider taking doses.
            Minimum value: 0.0416667
            Maximum value: 3.40282e+38
            Default value: 3.40282e+38

        took_dose_event (str, optional):
            Event broadcast each time a person takes a dose.
            Default value: None

        common_intervention_parameters (CommonInterventionParameters, optional):
            The CommonInterventionParameters object that contains the 5 common
            parameters: cost, intervention_name, new_property_value, disqualifying_properties, dont_allow_duplicates.
            Default value: None
    """

    def __init__(self,
                 campaign: api_campaign,
                 adherence_config: AbstractWaningConfig,
                 doses: list,
                 non_adherence_options: list,
                 non_adherence_distribution: list,
                 dose_interval: float = 1,
                 max_dose_consideration_duration: float = 3.40282e+38,
                 took_dose_event: str = None,
                 common_intervention_parameters: CommonInterventionParameters = None):
        super().__init__(campaign, 'AdherentDrug', common_intervention_parameters)

        if not isinstance(adherence_config, AbstractWaningConfig):
            raise ValueError(f"adherence_config must be an instance of AbstractWaningConfig, not {type(adherence_config)}.")

        if not doses:
            raise ValueError("'doses' must be a non-empty list of lists of drug name strings.")
        for i, dose in enumerate(doses):
            if not isinstance(dose, list) or not all(isinstance(d, str) for d in dose):
                raise ValueError(f"doses[{i}] must be a list of strings.")

        if len(non_adherence_options) != len(non_adherence_distribution):
            raise ValueError("'non_adherence_options' and 'non_adherence_distribution' must have the same length.")
        if not non_adherence_options:
            raise ValueError("'non_adherence_options' must be a non-empty list.")
        if abs(sum(non_adherence_distribution) - 1.0) > 1e-6:
            raise ValueError(f"'non_adherence_distribution' values must sum to 1, got {sum(non_adherence_distribution)}.")

        self._intervention.Adherence_Config = adherence_config.to_schema_dict(campaign)
        self._intervention.Doses = doses
        self._intervention.Non_Adherence_Options = non_adherence_options
        self._intervention.Non_Adherence_Distribution = non_adherence_distribution
        self._intervention.Dose_Interval = validate_value_range(dose_interval, 'dose_interval', 0, 100000, float)
        self._intervention.Max_Dose_Consideration_Duration = validate_value_range(max_dose_consideration_duration, 'max_dose_consideration_duration', 0.0416667, 3.40282e+38, float)
        self._intervention.Took_Dose_Event = set_event(took_dose_event, 'took_dose_event', campaign, True)


class BitingRisk(IndividualIntervention):
    """
    The **BitingRisk** intervention class assigns a relative risk of mosquito biting to an individual,
    drawn from a configurable distribution. This modifies how likely the individual is to be bitten
    relative to others in their node.

    Args:
        campaign (api_campaign, required):
            An instance of the emod_api.campaign module.

        risk_distribution (BaseDistribution, required):
            Distribution used to assign each individual's relative biting risk. Use one of the
            following distribution classes from emodpy_hiv.utils.distributions:
            * ConstantDistribution
            * UniformDistribution
            * GaussianDistribution
            * ExponentialDistribution
            * PoissonDistribution
            * LogNormalDistribution
            * DualConstantDistribution
            * WeibullDistribution
            * DualExponentialDistribution

        common_intervention_parameters (CommonInterventionParameters, optional):
            The CommonInterventionParameters object that contains the 5 common
            parameters: cost, intervention_name, new_property_value, disqualifying_properties, dont_allow_duplicates.
            Default value: None
    """

    def __init__(self,
                 campaign: api_campaign,
                 risk_distribution: BaseDistribution,
                 common_intervention_parameters: CommonInterventionParameters = None):
        super().__init__(campaign, 'BitingRisk', common_intervention_parameters)

        if not isinstance(risk_distribution, BaseDistribution):
            raise ValueError(f"risk_distribution must be an instance of BaseDistribution, not {type(risk_distribution)}.")
        self.set_distribution(risk_distribution, 'Risk')


class HumanHostSeekingTrap(IndividualIntervention):
    """
    The **HumanHostSeekingTrap** intervention class places a trap on an individual that attracts and
    kills host-seeking vectors before they can feed.

    Args:
        campaign (api_campaign, required):
            An instance of the emod_api.campaign module.

        attract_config (AbstractWaningConfig, required):
            Configuration of attraction efficacy and waning. Determines the fraction of host-seeking
            vectors that are attracted to the trap instead of finding a human host. Specify how this
            effect decays over time using one of the Waning Config classes in
            emodpy_hiv.campaign.waning_config.

        killing_config (AbstractWaningConfig, required):
            Configuration of killing efficacy and waning. Only vectors attracted to the trap via
            **attract_config** are targeted. Specify how this effect decays over time using one of the
            Waning Config classes in emodpy_hiv.campaign.waning_config.

        common_intervention_parameters (CommonInterventionParameters, optional):
            The CommonInterventionParameters object that contains the 5 common
            parameters: cost, intervention_name, new_property_value, disqualifying_properties, dont_allow_duplicates.
            Default value: None
    """

    def __init__(self,
                 campaign: api_campaign,
                 attract_config: AbstractWaningConfig,
                 killing_config: AbstractWaningConfig,
                 common_intervention_parameters: CommonInterventionParameters = None):
        super().__init__(campaign, 'HumanHostSeekingTrap', common_intervention_parameters)

        for param_name, waning in [('attract_config', attract_config),
                                   ('killing_config', killing_config)]:
            if not isinstance(waning, AbstractWaningConfig):
                raise ValueError(f"'{param_name}' must be an instance of AbstractWaningConfig, not {type(waning)}.")

        self._intervention.Attract_Config = attract_config.to_schema_dict(campaign)
        self._intervention.Killing_Config = killing_config.to_schema_dict(campaign)


class Ivermectin(IndividualIntervention):
    """
    The **Ivermectin** intervention class distributes ivermectin to an individual, which kills
    vectors that feed on them.

    Args:
        campaign (api_campaign, required):
            An instance of the emod_api.campaign module.

        killing_config (AbstractWaningConfig, required):
            Configuration of killing efficacy and waning over time for vectors that feed on the
            individual. Specify how this effect decays over time using one of the Waning Config
            classes in emodpy_hiv.campaign.waning_config.

        insecticide_name (str, optional):
            The name of the insecticide defined in the configuration parameter **Insecticides** for
            this intervention. If insecticides are not being used, this can be left empty.
            Default value: None

        common_intervention_parameters (CommonInterventionParameters, optional):
            The CommonInterventionParameters object that contains the 5 common
            parameters: cost, intervention_name, new_property_value, disqualifying_properties, dont_allow_duplicates.
            Default value: None
    """

    def __init__(self,
                 campaign: api_campaign,
                 killing_config: AbstractWaningConfig,
                 insecticide_name: str = None,
                 common_intervention_parameters: CommonInterventionParameters = None):
        super().__init__(campaign, 'Ivermectin', common_intervention_parameters)

        if not isinstance(killing_config, AbstractWaningConfig):
            raise ValueError(f"killing_config must be an instance of AbstractWaningConfig, not {type(killing_config)}.")

        self._intervention.Killing_Config = killing_config.to_schema_dict(campaign)

        if insecticide_name is not None:
            self._intervention.Insecticide_Name = insecticide_name


class IndoorIndividualEmanator(IndividualIntervention):
    """
    The **IndoorIndividualEmanator** intervention class applies a personal indoor emanating device
    (such as a spatial repellent) that repels and/or kills vectors indoors.

    Args:
        campaign (api_campaign, required):
            An instance of the emod_api.campaign module.

        killing_config (AbstractWaningConfig, required):
            Configuration of killing efficacy and waning. Killing is conditional on the vector not
            being repelled first. Specify how this effect decays over time using one of the Waning
            Config classes in emodpy_hiv.campaign.waning_config.

        repelling_config (AbstractWaningConfig, required):
            Configuration of repelling efficacy and waning. A vector is repelled before any killing
            can occur. Specify how this effect decays over time using one of the Waning Config
            classes in emodpy_hiv.campaign.waning_config.

        insecticide_name (str, optional):
            The name of the insecticide defined in the configuration parameter **Insecticides** for
            this intervention. If insecticides are not being used, this can be left empty.
            Default value: None

        common_intervention_parameters (CommonInterventionParameters, optional):
            The CommonInterventionParameters object that contains the 5 common
            parameters: cost, intervention_name, new_property_value, disqualifying_properties, dont_allow_duplicates.
            Default value: None
    """

    def __init__(self,
                 campaign: api_campaign,
                 killing_config: AbstractWaningConfig,
                 repelling_config: AbstractWaningConfig,
                 insecticide_name: str = None,
                 common_intervention_parameters: CommonInterventionParameters = None):
        super().__init__(campaign, 'IndoorIndividualEmanator', common_intervention_parameters)

        for param_name, waning in [('killing_config', killing_config),
                                   ('repelling_config', repelling_config)]:
            if not isinstance(waning, AbstractWaningConfig):
                raise ValueError(f"'{param_name}' must be an instance of AbstractWaningConfig, not {type(waning)}.")

        self._intervention.Killing_Config = killing_config.to_schema_dict(campaign)
        self._intervention.Repelling_Config = repelling_config.to_schema_dict(campaign)

        if insecticide_name is not None:
            self._intervention.Insecticide_Name = insecticide_name


class MultiInsecticideUsageDependentBednet(IndividualIntervention):
    """
    The **MultiInsecticideUsageDependentBednet** intervention class distributes a bed net with
    multiple insecticides, each with independent repelling, blocking, and killing waning effects.
    Net usage varies over time and the net expires after a duration drawn from a configurable
    distribution.

    Args:
        campaign (api_campaign, required):
            An instance of the emod_api.campaign module.

        insecticides (list[InsecticideWaningEffectRBK], required):
            A list of per-insecticide repelling, blocking, and killing waning effect definitions.
            Each element must be an **InsecticideWaningEffectRBK** instance.

        usage_config_list (list[AbstractWaningConfig], required):
            A list of WaningEffects whose effects are multiplied together to determine the overall
            usage effect. Use one of the Waning Config classes from emodpy_hiv.campaign.waning_config.

        expiration_period_distribution (BaseDistribution, required):
            Distribution determining how long the bed net lasts before expiring. Use one of the
            following distribution classes from emodpy_hiv.utils.distributions:
            * ConstantDistribution
            * UniformDistribution
            * GaussianDistribution
            * ExponentialDistribution
            * PoissonDistribution
            * LogNormalDistribution
            * DualConstantDistribution
            * WeibullDistribution
            * DualExponentialDistribution

        received_event (str, optional):
            The event broadcast when a new net is received (first net or replacement).
            Default value: None

        using_event (str, optional):
            The event broadcast each time step in which the bed net is being used.
            Default value: None

        discard_event (str, optional):
            The event broadcast when an individual discards their bed net, either by replacing it
            or due to the expiration timer.
            Default value: None

        common_intervention_parameters (CommonInterventionParameters, optional):
            The CommonInterventionParameters object that contains the 5 common
            parameters: cost, intervention_name, new_property_value, disqualifying_properties, dont_allow_duplicates.
            Default value: None
    """

    def __init__(self,
                 campaign: api_campaign,
                 insecticides: list,
                 usage_config_list: list,
                 expiration_period_distribution: BaseDistribution,
                 received_event: str = None,
                 using_event: str = None,
                 discard_event: str = None,
                 common_intervention_parameters: CommonInterventionParameters = None):
        super().__init__(campaign, 'MultiInsecticideUsageDependentBednet', common_intervention_parameters)

        if not insecticides:
            raise ValueError("'insecticides' must be a non-empty list of InsecticideWaningEffectRBK instances.")
        for i, ins in enumerate(insecticides):
            if not isinstance(ins, InsecticideWaningEffectRBK):
                raise ValueError(f"'insecticides[{i}]' must be an instance of InsecticideWaningEffectRBK, not {type(ins)}.")

        if not usage_config_list:
            raise ValueError("'usage_config_list' must be a non-empty list of AbstractWaningConfig instances.")
        for i, waning in enumerate(usage_config_list):
            if not isinstance(waning, AbstractWaningConfig):
                raise ValueError(f"'usage_config_list[{i}]' must be an instance of AbstractWaningConfig, not {type(waning)}.")

        if not isinstance(expiration_period_distribution, BaseDistribution):
            raise ValueError(f"expiration_period_distribution must be an instance of BaseDistribution, not {type(expiration_period_distribution)}.")

        self._intervention.Insecticides = [ins.to_schema_dict(campaign) for ins in insecticides]
        self._intervention.Usage_Config_List = [w.to_schema_dict(campaign) for w in usage_config_list]
        self.set_distribution(expiration_period_distribution, 'Expiration_Period')
        self._intervention.Received_Event = set_event(received_event, 'received_event', campaign, True)
        self._intervention.Using_Event = set_event(using_event, 'using_event', campaign, True)
        self._intervention.Discard_Event = set_event(discard_event, 'discard_event', campaign, True)


class MultiInsecticideIRSHousingModification(IndividualIntervention):
    """
    The **MultiInsecticideIRSHousingModification** intervention class applies indoor residual spraying
    with multiple insecticides to an individual's housing. Each insecticide has independent repelling
    and killing waning effects.

    Args:
        campaign (api_campaign, required):
            An instance of the emod_api.campaign module.

        insecticides (list[InsecticideWaningEffectRK], required):
            A list of per-insecticide repelling and killing waning effect definitions. Each element
            must be an **InsecticideWaningEffectRK** instance.

        common_intervention_parameters (CommonInterventionParameters, optional):
            The CommonInterventionParameters object that contains the 5 common
            parameters: cost, intervention_name, new_property_value, disqualifying_properties, dont_allow_duplicates.
            Default value: None
    """

    def __init__(self,
                 campaign: api_campaign,
                 insecticides: list,
                 common_intervention_parameters: CommonInterventionParameters = None):
        super().__init__(campaign, 'MultiInsecticideIRSHousingModification', common_intervention_parameters)

        if not insecticides:
            raise ValueError("'insecticides' must be a non-empty list of InsecticideWaningEffectRK instances.")
        for i, ins in enumerate(insecticides):
            if not isinstance(ins, InsecticideWaningEffectRK):
                raise ValueError(f"'insecticides[{i}]' must be an instance of InsecticideWaningEffectRK, not {type(ins)}.")

        self._intervention.Insecticides = [ins.to_schema_dict(campaign) for ins in insecticides]


class SimpleHousingModification(IndividualIntervention):
    """
    The **SimpleHousingModification** intervention class applies a simple housing modification that
    repels and/or kills vectors, such as screening or insecticide treatment of walls.

    Args:
        campaign (api_campaign, required):
            An instance of the emod_api.campaign module.

        killing_config (AbstractWaningConfig, required):
            Configuration of killing efficacy and waning. Killing is conditional on the vector not
            being repelled first. Specify how this effect decays over time using one of the Waning
            Config classes in emodpy_hiv.campaign.waning_config.

        repelling_config (AbstractWaningConfig, required):
            Configuration of repelling efficacy and waning. A vector is repelled before any killing
            can occur. Specify how this effect decays over time using one of the Waning Config
            classes in emodpy_hiv.campaign.waning_config.

        insecticide_name (str, optional):
            The name of the insecticide defined in the configuration parameter **Insecticides** for
            this intervention. If insecticides are not being used, this can be left empty.
            Default value: None

        common_intervention_parameters (CommonInterventionParameters, optional):
            The CommonInterventionParameters object that contains the 5 common
            parameters: cost, intervention_name, new_property_value, disqualifying_properties, dont_allow_duplicates.
            Default value: None
    """

    def __init__(self,
                 campaign: api_campaign,
                 killing_config: AbstractWaningConfig,
                 repelling_config: AbstractWaningConfig,
                 insecticide_name: str = None,
                 common_intervention_parameters: CommonInterventionParameters = None):
        super().__init__(campaign, 'SimpleHousingModification', common_intervention_parameters)

        for param_name, waning in [('killing_config', killing_config),
                                   ('repelling_config', repelling_config)]:
            if not isinstance(waning, AbstractWaningConfig):
                raise ValueError(f"'{param_name}' must be an instance of AbstractWaningConfig, not {type(waning)}.")

        self._intervention.Killing_Config = killing_config.to_schema_dict(campaign)
        self._intervention.Repelling_Config = repelling_config.to_schema_dict(campaign)

        if insecticide_name is not None:
            self._intervention.Insecticide_Name = insecticide_name


class SimpleIndividualRepellent(IndividualIntervention):
    """
    The **SimpleIndividualRepellent** intervention class applies a personal repellent to an individual
    (such as DEET or picaridin) that reduces the probability of mosquito feeding.

    Args:
        campaign (api_campaign, required):
            An instance of the emod_api.campaign module.

        repelling_config (AbstractWaningConfig, required):
            Configuration of repelling efficacy and waning. Specify how this effect decays over time
            using one of the Waning Config classes in emodpy_hiv.campaign.waning_config.

        insecticide_name (str, optional):
            The name of the insecticide defined in the configuration parameter **Insecticides** for
            this intervention. If insecticides are not being used, this can be left empty.
            Default value: None

        common_intervention_parameters (CommonInterventionParameters, optional):
            The CommonInterventionParameters object that contains the 5 common
            parameters: cost, intervention_name, new_property_value, disqualifying_properties, dont_allow_duplicates.
            Default value: None
    """

    def __init__(self,
                 campaign: api_campaign,
                 repelling_config: AbstractWaningConfig,
                 insecticide_name: str = None,
                 common_intervention_parameters: CommonInterventionParameters = None):
        super().__init__(campaign, 'SimpleIndividualRepellent', common_intervention_parameters)

        if not isinstance(repelling_config, AbstractWaningConfig):
            raise ValueError(f"repelling_config must be an instance of AbstractWaningConfig, not {type(repelling_config)}.")

        self._intervention.Repelling_Config = repelling_config.to_schema_dict(campaign)

        if insecticide_name is not None:
            self._intervention.Insecticide_Name = insecticide_name


class SpatialRepellentHousingModification(IndividualIntervention):
    """
    The **SpatialRepellentHousingModification** intervention class applies a spatial repellent to an
    individual's housing (such as a passive emanator), reducing the probability that host-seeking
    vectors approach and enter the dwelling.

    Args:
        campaign (api_campaign, required):
            An instance of the emod_api.campaign module.

        repelling_config (AbstractWaningConfig, required):
            Configuration of repelling efficacy and waning. Specify how this effect decays over time
            using one of the Waning Config classes in emodpy_hiv.campaign.waning_config.

        insecticide_name (str, optional):
            The name of the insecticide defined in the configuration parameter **Insecticides** for
            this intervention. If insecticides are not being used, this can be left empty.
            Default value: None

        common_intervention_parameters (CommonInterventionParameters, optional):
            The CommonInterventionParameters object that contains the 5 common
            parameters: cost, intervention_name, new_property_value, disqualifying_properties, dont_allow_duplicates.
            Default value: None
    """

    def __init__(self,
                 campaign: api_campaign,
                 repelling_config: AbstractWaningConfig,
                 insecticide_name: str = None,
                 common_intervention_parameters: CommonInterventionParameters = None):
        super().__init__(campaign, 'SpatialRepellentHousingModification', common_intervention_parameters)

        if not isinstance(repelling_config, AbstractWaningConfig):
            raise ValueError(f"repelling_config must be an instance of AbstractWaningConfig, not {type(repelling_config)}.")

        self._intervention.Repelling_Config = repelling_config.to_schema_dict(campaign)

        if insecticide_name is not None:
            self._intervention.Insecticide_Name = insecticide_name


class OutbreakIndividualMalariaGenetics(IndividualIntervention):
    """
    The **OutbreakIndividualMalariaGenetics** intervention class force-infects individuals with a
    malaria parasite whose genome is specified via barcode string, allele frequencies, or a full
    nucleotide sequence. Used in conjunction with the **Parasite_Genetics** configuration parameters.

    Args:
        campaign (api_campaign, required):
            An instance of the emod_api.campaign module.

        create_nucleotide_sequence_from (CreateNucleotideSequenceFrom, optional):
            Indicates how the genome is created. Possible values are:
            * CreateNucleotideSequenceFrom.BARCODE_STRING — specify genome via barcode; use with
              **barcode_string** and optionally **drug_resistant_string** and **hrp_string**.
            * CreateNucleotideSequenceFrom.ALLELE_FREQUENCIES — genome created randomly using
              frequencies in **barcode_allele_frequencies_per_genome_location** and related params.
            * CreateNucleotideSequenceFrom.NUCLEOTIDE_SEQUENCE — specify full nucleotide sequence;
              use with **barcode_string**, **drug_resistant_string**, **hrp_string**,
              **msp_variant_value**, and **pfemp1_variants_values**.
            Default value: CreateNucleotideSequenceFrom.BARCODE_STRING

        barcode_string (str, optional):
            A string of nucleotide base letters (A, C, G, T) representing the barcode genome
            locations. Required when **create_nucleotide_sequence_from** is BARCODE_STRING or
            NUCLEOTIDE_SEQUENCE.
            Default value: None

        drug_resistant_string (str, optional):
            A string of nucleotide base letters (A, C, G, T) representing drug-resistant genome
            locations. Required when **create_nucleotide_sequence_from** is BARCODE_STRING or
            NUCLEOTIDE_SEQUENCE.
            Default value: None

        hrp_string (str, optional):
            A string of nucleotide base letters indicating HRP marker presence at each genome
            location ('A' = absent, non-'A' = present). Required when
            **create_nucleotide_sequence_from** is BARCODE_STRING or NUCLEOTIDE_SEQUENCE.
            Default value: None

        barcode_allele_frequencies_per_genome_location (list[list[float]], optional):
            2D array of allele frequencies per barcode genome location. Each inner list contains
            four values for alleles A, C, G, T. Required when **create_nucleotide_sequence_from**
            is ALLELE_FREQUENCIES.
            Default value: None

        drug_resistant_allele_frequencies_per_genome_location (list[list[float]], optional):
            2D array of allele frequencies per drug-resistant genome location. Required when
            **create_nucleotide_sequence_from** is ALLELE_FREQUENCIES.
            Default value: None

        hrp_allele_frequencies_per_genome_location (list[list[float]], optional):
            2D array of allele frequencies per HRP genome location. Required when
            **create_nucleotide_sequence_from** is ALLELE_FREQUENCIES.
            Default value: None

        msp_variant_value (int, optional):
            The Merozoite Surface Protein variant value. Must be <= **Falciparum_MSP_Variants**.
            Required when **create_nucleotide_sequence_from** is NUCLEOTIDE_SEQUENCE.
            Minimum value: 0
            Maximum value: 1000
            Default value: 0

        pfemp1_variants_values (list[int], optional):
            Array of 50 PfEMP1 major epitope variant values. Each must be <=
            **Falciparum_PfEMP1_Variants**. Required when **create_nucleotide_sequence_from**
            is NUCLEOTIDE_SEQUENCE.
            Default value: None

        ignore_immunity (bool, optional):
            If True, individuals are force-infected regardless of their actual immunity level.
            Default value: True

        incubation_period_override (int, optional):
            Overrides the incubation period (days) from the configuration file. Set to -1 to
            use the configuration parameter settings.
            Minimum value: -1
            Maximum value: 2147480000
            Default value: -1
    """

    def __init__(self,
                 campaign: api_campaign,
                 create_nucleotide_sequence_from: CreateNucleotideSequenceFrom = CreateNucleotideSequenceFrom.BARCODE_STRING,
                 barcode_string: str = None,
                 drug_resistant_string: str = None,
                 hrp_string: str = None,
                 barcode_allele_frequencies_per_genome_location: list = None,
                 drug_resistant_allele_frequencies_per_genome_location: list = None,
                 hrp_allele_frequencies_per_genome_location: list = None,
                 msp_variant_value: int = 0,
                 pfemp1_variants_values: list = None,
                 ignore_immunity: bool = True,
                 incubation_period_override: int = -1):
        super().__init__(campaign, 'OutbreakIndividualMalariaGenetics')

        self._intervention.Create_Nucleotide_Sequence_From = create_nucleotide_sequence_from
        self._intervention.Ignore_Immunity = 1 if ignore_immunity else 0
        self._intervention.Incubation_Period_Override = validate_value_range(incubation_period_override, 'incubation_period_override', -1, 2147480000, int)

        if create_nucleotide_sequence_from in (CreateNucleotideSequenceFrom.BARCODE_STRING,
                                               CreateNucleotideSequenceFrom.NUCLEOTIDE_SEQUENCE):
            if barcode_string is not None:
                self._intervention.Barcode_String = barcode_string
            if drug_resistant_string is not None:
                self._intervention.Drug_Resistant_String = drug_resistant_string
            if hrp_string is not None:
                self._intervention.HRP_String = hrp_string

        if create_nucleotide_sequence_from == CreateNucleotideSequenceFrom.NUCLEOTIDE_SEQUENCE:
            self._intervention.MSP_Variant_Value = validate_value_range(msp_variant_value, 'msp_variant_value', 0, 1000, int)
            if pfemp1_variants_values is not None:
                self._intervention.PfEMP1_Variants_Values = pfemp1_variants_values

        if create_nucleotide_sequence_from == CreateNucleotideSequenceFrom.ALLELE_FREQUENCIES:
            if barcode_allele_frequencies_per_genome_location is not None:
                self._intervention.Barcode_Allele_Frequencies_Per_Genome_Location = barcode_allele_frequencies_per_genome_location
            if drug_resistant_allele_frequencies_per_genome_location is not None:
                self._intervention.Drug_Resistant_Allele_Frequencies_Per_Genome_Location = drug_resistant_allele_frequencies_per_genome_location
            if hrp_allele_frequencies_per_genome_location is not None:
                self._intervention.HRP_Allele_Frequencies_Per_Genome_Location = hrp_allele_frequencies_per_genome_location


class OutbreakIndividualMalariaVarGenes(IndividualIntervention):
    """
    The **OutbreakIndividualMalariaVarGenes** intervention class force-infects individuals with a
    malaria parasite whose antigenic properties (MSP type, IRBC type, minor epitope type) are
    explicitly specified. Used when tracking variant gene-based immunity.

    Args:
        campaign (api_campaign, required):
            An instance of the emod_api.campaign module.

        msp_type (int, optional):
            The Merozoite Surface Protein variant value of the infection. Must be <=
            **Falciparum_MSP_Variants**.
            Minimum value: 0
            Maximum value: 1000
            Default value: 0

        irbc_type (list[int], optional):
            Array of 50 PfEMP1 major epitope variant values. Each must be <=
            **Falciparum_PfEMP1_Variants**.
            Default value: None

        minor_epitope_type (list[int], optional):
            Array of 50 PfEMP1 minor epitope variant values. Each must be <=
            **Falciparum_Nonspecific_Types** * 5.
            Default value: None

        ignore_immunity (bool, optional):
            If True, individuals are force-infected regardless of their actual immunity level.
            Default value: True

        incubation_period_override (int, optional):
            Overrides the incubation period (days) from the configuration file. Set to -1 to
            use the configuration parameter settings.
            Minimum value: -1
            Maximum value: 2147480000
            Default value: -1
    """

    def __init__(self,
                 campaign: api_campaign,
                 msp_type: int = 0,
                 irbc_type: list = None,
                 minor_epitope_type: list = None,
                 ignore_immunity: bool = True,
                 incubation_period_override: int = -1):
        super().__init__(campaign, 'OutbreakIndividualMalariaVarGenes')

        self._intervention.MSP_Type = validate_value_range(msp_type, 'msp_type', 0, 1000, int)
        self._intervention.Ignore_Immunity = 1 if ignore_immunity else 0
        self._intervention.Incubation_Period_Override = validate_value_range(incubation_period_override, 'incubation_period_override', -1, 2147480000, int)

        if irbc_type is not None:
            self._intervention.IRBC_Type = irbc_type
        if minor_epitope_type is not None:
            self._intervention.Minor_Epitope_Type = minor_epitope_type


# __all_exports: A list of classes that are intended to be exported from this module.
__all_exports = [
    CreateNucleotideSequenceFrom,
    MalariaChallengeType,
    MalariaDiagnosticType,
    NonAdherenceOption,
    InsecticideWaningEffectRBK,
    InsecticideWaningEffectRK,
    AdherentDrug,
    AntimalarialDrug,
    BitingRisk,
    HumanHostSeekingTrap,
    IndoorIndividualEmanator,
    IRSHousingModification,
    Ivermectin,
    MalariaChallenge,
    MalariaDiagnostic,
    MultiInsecticideIRSHousingModification,
    MultiInsecticideUsageDependentBednet,
    OutbreakIndividualMalariaGenetics,
    OutbreakIndividualMalariaVarGenes,
    RTSSVaccine,
    SimpleBednet,
    SimpleHousingModification,
    SimpleIndividualRepellent,
    SpatialRepellentHousingModification,
    UsageDependentBednet,
]

# The following loop sets the __module__ attribute of each class in __all_exports to the name of the current module.
# This is done to ensure that when these classes are imported from this module, their __module__ attribute correctly
# reflects their source module.

for _ in __all_exports:
    _.__module__ = __name__

# __all__: A list that defines the public interface of this module.
# This is essential to ensure that Sphinx builds documentation for these classes, including those that are imported
# from emodpy.
# It contains the names of all the classes that should be accessible when this module is imported using the syntax
# 'from module import *'.
# Here, it is set to the names of all classes in __all_exports.

__all__ = [_.__name__ for _ in __all_exports]
