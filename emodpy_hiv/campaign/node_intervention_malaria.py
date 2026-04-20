import emod_api.schema_to_class as s2c
from emodpy.campaign.base_intervention import NodeIntervention
from emodpy.campaign.common import CommonInterventionParameters
from emodpy.utils import validate_value_range
from emodpy_hiv.utils.emod_enum import StrEnum
from emodpy_hiv.campaign.waning_config import AbstractWaningConfig
from emodpy_hiv.utils.distributions import BaseDistribution
from emod_api import campaign as api_campaign


class ArtificialDietTarget(StrEnum):
    AD_WITHIN_VILLAGE = 'AD_WithinVillage'
    AD_OUTSIDE_VILLAGE = 'AD_OutsideVillage'


class EIRType(StrEnum):
    MONTHLY = 'MONTHLY'
    DAILY = 'DAILY'


class HabitatType(StrEnum):
    NONE = 'NONE'
    TEMPORARY_RAINFALL = 'TEMPORARY_RAINFALL'
    WATER_VEGETATION = 'WATER_VEGETATION'
    HUMAN_POPULATION = 'HUMAN_POPULATION'
    CONSTANT = 'CONSTANT'
    BRACKISH_SWAMP = 'BRACKISH_SWAMP'
    LINEAR_SPLINE = 'LINEAR_SPLINE'
    ALL_HABITATS = 'ALL_HABITATS'


class MalariaChallengeType(StrEnum):
    INFECTIOUS_BITES = 'InfectiousBites'
    SPOROZOITES = 'Sporozoites'


class ReleasedType(StrEnum):
    FIXED_NUMBER = 'FIXED_NUMBER'
    RATIO = 'RATIO'


class ReleasedWolbachia(StrEnum):
    VECTOR_WOLBACHIA_FREE = 'VECTOR_WOLBACHIA_FREE'
    VECTOR_WOLBACHIA_A = 'VECTOR_WOLBACHIA_A'
    VECTOR_WOLBACHIA_B = 'VECTOR_WOLBACHIA_B'
    VECTOR_WOLBACHIA_AB = 'VECTOR_WOLBACHIA_AB'


class InsecticideWaningEffectK:
    """
    Defines per-insecticide killing waning effect for use in **MultiInsecticideIndoorSpaceSpraying**
    and **MultiInsecticideSpaceSpraying**. Each element in the **Insecticides** array of those
    interventions is an instance of this class.

    Args:
        insecticide_name (str, required):
            The name of the insecticide defined in the configuration parameter **Insecticides**.

        killing_config (AbstractWaningConfig, required):
            The configuration of killing efficacy and waning for this insecticide. Specify how
            this effect decays over time using one of the Waning Config classes in
            emodpy_hiv.campaign.waning_config.
    """

    def __init__(self,
                 insecticide_name: str,
                 killing_config: AbstractWaningConfig):
        if not insecticide_name:
            raise ValueError("'insecticide_name' must be a non-empty string.")
        if not isinstance(killing_config, AbstractWaningConfig):
            raise ValueError(f"'killing_config' must be an instance of AbstractWaningConfig, not {type(killing_config)}.")
        self.insecticide_name = insecticide_name
        self.killing_config = killing_config

    def to_schema_dict(self, campaign) -> s2c.ReadOnlyDict:
        iew = s2c.get_class_with_defaults("idmType:InsecticideWaningEffect_K", schema_json=campaign.get_schema())
        iew.Insecticide_Name = self.insecticide_name
        iew.Killing_Config = self.killing_config.to_schema_dict(campaign)
        iew.finalize()
        return iew


class LarvalHabitatMultiplierSpec:
    """
    Defines a single larval habitat multiplier specification for use in **ScaleLarvalHabitat**.
    Each element in the **Larval_Habitat_Multiplier** array is an instance of this class.

    Args:
        factor (float, required):
            The multiplier by which to scale the larval habitat availability.
            Minimum value: 0
            Maximum value: 3.40282e+38

        habitat (HabitatType, optional):
            The larval habitat type to target. Possible values are:
            * NONE (default but not allowed; must be set to a specific habitat type)
            * TEMPORARY_RAINFALL
            * WATER_VEGETATION
            * HUMAN_POPULATION
            * CONSTANT
            * BRACKISH_SWAMP
            * LINEAR_SPLINE
            * ALL_HABITATS
            Default value: HabitatType.ALL_HABITATS

        species (str, optional):
            The name of the mosquito species to target. This must match a name in the
            configuration parameter **Vector_Species_Params** or be set to 'ALL_SPECIES'.
            Default value: 'ALL_SPECIES'
    """

    def __init__(self,
                 factor: float,
                 habitat: HabitatType = HabitatType.ALL_HABITATS,
                 species: str = 'ALL_SPECIES'):
        self.factor = validate_value_range(factor, 'factor', 0, 3.40282e+38, float)
        self.habitat = str(habitat)
        self.species = species

    def to_schema_dict(self, campaign) -> s2c.ReadOnlyDict:
        spec = s2c.get_class_with_defaults("idmType:LarvalHabitatMultiplierSpec", schema_json=campaign.get_schema())
        spec.Factor = self.factor
        spec.Habitat = self.habitat
        spec.Species = self.species
        spec.finalize()
        return spec


class AnimalFeedKill(NodeIntervention):
    """
    The **AnimalFeedKill** node intervention class kills vectors that feed on animals in the node.
    It applies a configurable killing waning effect to vectors that take a blood meal from an
    animal host.

    Args:
        campaign (api_campaign, required):
            An instance of the emod_api.campaign module.

        killing_config (AbstractWaningConfig, required):
            The configuration of killing efficacy of the intervention. Specify how this effect
            decays over time using one of the Waning Config classes in
            emodpy_hiv.campaign.waning_config.

        insecticide_name (str, optional):
            The name of the insecticide defined in the configuration parameter **Insecticides**
            for this intervention. If insecticides are not being used, this can be left empty.
            Default value: None

        common_intervention_parameters (CommonInterventionParameters, optional):
            The CommonInterventionParameters object that contains the 5 common
            parameters: cost, intervention_name, new_property_value, disqualifying_properties,
            dont_allow_duplicates.
            Default value: None
    """

    def __init__(self,
                 campaign: api_campaign,
                 killing_config: AbstractWaningConfig,
                 insecticide_name: str = None,
                 common_intervention_parameters: CommonInterventionParameters = None):
        super().__init__(campaign, 'AnimalFeedKill', common_intervention_parameters)

        if not isinstance(killing_config, AbstractWaningConfig):
            raise ValueError(f"'killing_config' must be an instance of AbstractWaningConfig, not {type(killing_config)}.")
        self._intervention.Killing_Config = killing_config.to_schema_dict(campaign)

        if insecticide_name is not None:
            self._intervention.Insecticide_Name = insecticide_name


class ArtificialDiet(NodeIntervention):
    """
    The **ArtificialDiet** node intervention class diverts vectors from feeding on humans by
    providing an artificial diet source, either within the village or outside it.

    Args:
        campaign (api_campaign, required):
            An instance of the emod_api.campaign module.

        attraction_config (AbstractWaningConfig, required):
            The fraction of vector feeds attracted to the artificial diet and how that fraction
            wanes over time. Specify how this effect decays over time using one of the Waning
            Config classes in emodpy_hiv.campaign.waning_config.

        artificial_diet_target (ArtificialDietTarget, optional):
            The location of the artificial diet. Possible values are:
            * AD_WITHIN_VILLAGE
            * AD_OUTSIDE_VILLAGE
            Default value: ArtificialDietTarget.AD_WITHIN_VILLAGE

        common_intervention_parameters (CommonInterventionParameters, optional):
            The CommonInterventionParameters object that contains the 5 common
            parameters: cost, intervention_name, new_property_value, disqualifying_properties,
            dont_allow_duplicates.
            Default value: None
    """

    def __init__(self,
                 campaign: api_campaign,
                 attraction_config: AbstractWaningConfig,
                 artificial_diet_target: ArtificialDietTarget = ArtificialDietTarget.AD_WITHIN_VILLAGE,
                 common_intervention_parameters: CommonInterventionParameters = None):
        super().__init__(campaign, 'ArtificialDiet', common_intervention_parameters)

        if not isinstance(attraction_config, AbstractWaningConfig):
            raise ValueError(f"'attraction_config' must be an instance of AbstractWaningConfig, not {type(attraction_config)}.")
        self._intervention.Attraction_Config = attraction_config.to_schema_dict(campaign)
        self._intervention.Artificial_Diet_Target = str(artificial_diet_target)


class IndoorSpaceSpraying(NodeIntervention):
    """
    The **IndoorSpaceSpraying** node intervention class applies indoor space spraying to kill
    mosquitoes inside dwellings in the node. The proportion of the node sprayed is controlled
    by **spray_coverage**.

    Args:
        campaign (api_campaign, required):
            An instance of the emod_api.campaign module.

        killing_config (AbstractWaningConfig, required):
            The configuration of killing efficacy of the intervention. Specify how this effect
            decays over time using one of the Waning Config classes in
            emodpy_hiv.campaign.waning_config.

        spray_coverage (float, optional):
            The proportion of the node that has been sprayed. This value is multiplied by the
            current efficacy of the waning effect.
            Minimum value: 0
            Maximum value: 1
            Default value: 1

        insecticide_name (str, optional):
            The name of the insecticide defined in the configuration parameter **Insecticides**
            for this intervention. If insecticides are not being used, this can be left empty.
            Default value: None

        common_intervention_parameters (CommonInterventionParameters, optional):
            The CommonInterventionParameters object that contains the 5 common
            parameters: cost, intervention_name, new_property_value, disqualifying_properties,
            dont_allow_duplicates.
            Default value: None
    """

    def __init__(self,
                 campaign: api_campaign,
                 killing_config: AbstractWaningConfig,
                 spray_coverage: float = 1,
                 insecticide_name: str = None,
                 common_intervention_parameters: CommonInterventionParameters = None):
        super().__init__(campaign, 'IndoorSpaceSpraying', common_intervention_parameters)

        if not isinstance(killing_config, AbstractWaningConfig):
            raise ValueError(f"'killing_config' must be an instance of AbstractWaningConfig, not {type(killing_config)}.")
        self._intervention.Killing_Config = killing_config.to_schema_dict(campaign)
        self._intervention.Spray_Coverage = validate_value_range(spray_coverage, 'spray_coverage', 0, 1, float)

        if insecticide_name is not None:
            self._intervention.Insecticide_Name = insecticide_name


class InputEIR(NodeIntervention):
    """
    The **InputEIR** node intervention class inputs a user-defined entomological inoculation rate
    (EIR) to the node. The EIR can be specified as 12 monthly values or 365 daily values.

    Note: This intervention is only supported in **MALARIA_SIM**.

    Args:
        campaign (api_campaign, required):
            An instance of the emod_api.campaign module.

        eir_type (EIRType, optional):
            Specifies whether the EIR is given as monthly or daily values. Possible values are:
            * MONTHLY — provide a list of 12 monthly EIR values via **monthly_eir**
            * DAILY   — provide a list of 365 daily EIR values via **daily_eir**
            Default value: EIRType.MONTHLY

        monthly_eir (list[float], conditional):
            An array of exactly 12 values where each value is the mean number of infectious bites
            for that month. Required when **eir_type** is MONTHLY. Note that the 'current month'
            is based on the time since the intervention was distributed, repeating on a 12-month
            cycle.
            Minimum value per element: 0
            Maximum value per element: 1000
            Default value: None

        daily_eir (list[float], conditional):
            An array of exactly 365 values where each value is the mean number of infectious bites
            for that day of the year. Required when **eir_type** is DAILY.
            Minimum value per element: 0
            Maximum value per element: 1000
            Default value: None

        scaling_factor (float, optional):
            A multiplier applied to the EIR value determined for the current day.
            Minimum value: 0
            Maximum value: 10000
            Default value: 1

        common_intervention_parameters (CommonInterventionParameters, optional):
            The CommonInterventionParameters object that contains the 4 common
            parameters: intervention_name, new_property_value, disqualifying_properties,
            dont_allow_duplicates.
            The following parameter is not valid for this intervention:
            cost
            Default value: None
    """

    def __init__(self,
                 campaign: api_campaign,
                 eir_type: EIRType = EIRType.MONTHLY,
                 monthly_eir: list[float] = None,
                 daily_eir: list[float] = None,
                 scaling_factor: float = 1,
                 common_intervention_parameters: CommonInterventionParameters = None):
        super().__init__(campaign, 'InputEIR', common_intervention_parameters)

        self._intervention.EIR_Type = str(eir_type)
        self._intervention.Scaling_Factor = validate_value_range(scaling_factor, 'scaling_factor', 0, 10000, float)

        if str(eir_type) == 'MONTHLY':
            if monthly_eir is None:
                raise ValueError("'monthly_eir' must be provided when eir_type is EIRType.MONTHLY.")
            if len(monthly_eir) != 12:
                raise ValueError(f"'monthly_eir' must have exactly 12 values, got {len(monthly_eir)}.")
            self._intervention.Monthly_EIR = monthly_eir.copy()
        else:  # DAILY
            if daily_eir is None:
                raise ValueError("'daily_eir' must be provided when eir_type is EIRType.DAILY.")
            if len(daily_eir) != 365:
                raise ValueError(f"'daily_eir' must have exactly 365 values, got {len(daily_eir)}.")
            self._intervention.Daily_EIR = daily_eir.copy()

    def _set_cost(self, cost: float) -> None:
        raise ValueError('Cost_To_Consumer is not a valid parameter for the InputEIR intervention.')


class LarvalMicrosporidiaIntervention(NodeIntervention):
    """
    The **LarvalMicrosporidiaIntervention** node intervention class introduces microsporidia into
    larval habitats in the node. Microsporidia are transmitted to larvae and can affect vector
    life expectancy and infection dynamics.

    Args:
        campaign (api_campaign, required):
            An instance of the emod_api.campaign module.

        infectivity_config (AbstractWaningConfig, required):
            Configures the probability that larvae acquire microsporidia from this intervention.
            Specify how this effect decays over time using one of the Waning Config classes in
            emodpy_hiv.campaign.waning_config.

        strain_name (str, optional):
            The name of the microsporidia strain to distribute. This must match a name defined
            in the configuration parameter **Strains_Param**.
            Default value: None

        habitat_coverage (float, optional):
            The proportion of habitat(s) affected by the intervention.
            Minimum value: 0
            Maximum value: 1
            Default value: 1

        habitat_target (HabitatType, optional):
            The larval habitat type targeted by the intervention. Possible values are:
            * NONE
            * TEMPORARY_RAINFALL
            * WATER_VEGETATION
            * HUMAN_POPULATION
            * CONSTANT
            * BRACKISH_SWAMP
            * LINEAR_SPLINE
            * ALL_HABITATS
            Default value: HabitatType.ALL_HABITATS

        common_intervention_parameters (CommonInterventionParameters, optional):
            The CommonInterventionParameters object that contains the 5 common
            parameters: cost, intervention_name, new_property_value, disqualifying_properties,
            dont_allow_duplicates.
            Default value: None
    """

    def __init__(self,
                 campaign: api_campaign,
                 infectivity_config: AbstractWaningConfig,
                 strain_name: str = None,
                 habitat_coverage: float = 1,
                 habitat_target: HabitatType = HabitatType.ALL_HABITATS,
                 common_intervention_parameters: CommonInterventionParameters = None):
        super().__init__(campaign, 'LarvalMicrosporidiaIntervention', common_intervention_parameters)

        if not isinstance(infectivity_config, AbstractWaningConfig):
            raise ValueError(f"'infectivity_config' must be an instance of AbstractWaningConfig, not {type(infectivity_config)}.")
        self._intervention.Infectivity_Config = infectivity_config.to_schema_dict(campaign)
        self._intervention.Habitat_Coverage = validate_value_range(habitat_coverage, 'habitat_coverage', 0, 1, float)
        self._intervention.Habitat_Target = str(habitat_target)

        if strain_name is not None:
            self._intervention.Strain_Name = strain_name


class Larvicides(NodeIntervention):
    """
    The **Larvicides** node intervention class kills larvae in targeted larval habitats using an
    insecticide. The killing efficacy wanes over time.

    Args:
        campaign (api_campaign, required):
            An instance of the emod_api.campaign module.

        larval_killing_config (AbstractWaningConfig, required):
            The configuration of killing efficacy and waning of larvae in the targeted habitat.
            Specify how this effect decays over time using one of the Waning Config classes in
            emodpy_hiv.campaign.waning_config.

        habitat_target (HabitatType, optional):
            The larval habitat type targeted for the intervention. Possible values are:
            * NONE (default but not allowed; must be set to a valid habitat type)
            * TEMPORARY_RAINFALL
            * WATER_VEGETATION
            * HUMAN_POPULATION
            * CONSTANT
            * BRACKISH_SWAMP
            * LINEAR_SPLINE
            * ALL_HABITATS
            Default value: HabitatType.ALL_HABITATS

        spray_coverage (float, optional):
            The proportion of the habitat(s) that will be affected by the intervention. This
            value is multiplied by the current efficacy of the waning effect.
            Minimum value: 0
            Maximum value: 1
            Default value: 1

        insecticide_name (str, optional):
            The name of the insecticide defined in the configuration parameter **Insecticides**
            for this intervention. If insecticides are not being used, this can be left empty.
            Default value: None

        common_intervention_parameters (CommonInterventionParameters, optional):
            The CommonInterventionParameters object that contains the 5 common
            parameters: cost, intervention_name, new_property_value, disqualifying_properties,
            dont_allow_duplicates.
            Default value: None
    """

    def __init__(self,
                 campaign: api_campaign,
                 larval_killing_config: AbstractWaningConfig,
                 habitat_target: HabitatType = HabitatType.ALL_HABITATS,
                 spray_coverage: float = 1,
                 insecticide_name: str = None,
                 common_intervention_parameters: CommonInterventionParameters = None):
        super().__init__(campaign, 'Larvicides', common_intervention_parameters)

        if not isinstance(larval_killing_config, AbstractWaningConfig):
            raise ValueError(f"'larval_killing_config' must be an instance of AbstractWaningConfig, not {type(larval_killing_config)}.")
        self._intervention.Larval_Killing_Config = larval_killing_config.to_schema_dict(campaign)
        self._intervention.Habitat_Target = str(habitat_target)
        self._intervention.Spray_Coverage = validate_value_range(spray_coverage, 'spray_coverage', 0, 1, float)

        if insecticide_name is not None:
            self._intervention.Insecticide_Name = insecticide_name


class MalariaChallenge(NodeIntervention):
    """
    The **MalariaChallenge** node intervention class challenges a fraction of individuals in the
    node with malaria via infectious bites or sporozoites. Unlike the individual-level
    **MalariaChallenge** in individual_intervention_malaria.py, this node-level version uses a
    **coverage** parameter to control what fraction of individuals in the node are challenged.

    Note: This intervention is only supported in **MALARIA_SIM**.

    Args:
        campaign (api_campaign, required):
            An instance of the emod_api.campaign module.

        challenge_type (MalariaChallengeType, optional):
            The type of malaria challenge. Possible values are:
            * INFECTIOUS_BITES — challenge via infectious bites (use with **infectious_bite_count**)
            * SPOROZOITES      — challenge via sporozoites (use with **sporozoite_count**)
            Default value: MalariaChallengeType.INFECTIOUS_BITES

        coverage (float, optional):
            The fraction of individuals in the node that receive the challenge.
            Minimum value: 0
            Maximum value: 1
            Default value: 1

        infectious_bite_count (int, optional):
            The number of infectious bites per challenged person. Used when **challenge_type** is
            INFECTIOUS_BITES.
            Minimum value: 0
            Maximum value: 1000
            Default value: 1

        sporozoite_count (int, optional):
            The number of sporozoites per challenged person. Used when **challenge_type** is
            SPOROZOITES.
            Minimum value: 0
            Maximum value: 1000
            Default value: 1

        common_intervention_parameters (CommonInterventionParameters, optional):
            The CommonInterventionParameters object that contains the 4 common
            parameters: intervention_name, new_property_value, disqualifying_properties,
            dont_allow_duplicates.
            The following parameter is not valid for this intervention:
            cost
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

        self._intervention.Challenge_Type = str(challenge_type)
        self._intervention.Coverage = validate_value_range(coverage, 'coverage', 0, 1, float)
        self._intervention.Infectious_Bite_Count = validate_value_range(infectious_bite_count, 'infectious_bite_count', 0, 1000, int)
        self._intervention.Sporozoite_Count = validate_value_range(sporozoite_count, 'sporozoite_count', 0, 1000, int)

    def _set_cost(self, cost: float) -> None:
        raise ValueError('Cost_To_Consumer is not a valid parameter for the MalariaChallenge intervention.')


class MosquitoRelease(NodeIntervention):
    """
    The **MosquitoRelease** node intervention class releases a fixed number or ratio of mosquitoes
    into the node. Released mosquitoes can carry Wolbachia, specific genomes, or microsporidia.

    Args:
        campaign (api_campaign, required):
            An instance of the emod_api.campaign module.

        released_species (str, required):
            The name of the mosquito species to release. This must match a name in the
            configuration parameter **Vector_Species_Params**.

        released_number (int, optional):
            The number of mosquitoes to release. Used when **released_type** is FIXED_NUMBER.
            Minimum value: 1
            Maximum value: 100000000
            Default value: 10000

        released_ratio (float, optional):
            The ratio of released mosquitoes to the existing population of the same gender from
            the previous timestep. Used when **released_type** is RATIO.
            Minimum value: 0
            Maximum value: 3.40282e+38
            Default value: 0.1

        released_type (ReleasedType, optional):
            Specifies how to determine the number of mosquitoes to release. Possible values are:
            * FIXED_NUMBER — release exactly **released_number** mosquitoes
            * RATIO        — release mosquitoes proportional to the current population
            Default value: ReleasedType.FIXED_NUMBER

        released_infectious (float, optional):
            The fraction of released mosquitoes that are infectious.
            Minimum value: 0
            Maximum value: 1
            Default value: 0

        released_wolbachia (ReleasedWolbachia, optional):
            The Wolbachia infection status of the released mosquitoes. Possible values are:
            * VECTOR_WOLBACHIA_FREE
            * VECTOR_WOLBACHIA_A
            * VECTOR_WOLBACHIA_B
            * VECTOR_WOLBACHIA_AB
            Default value: ReleasedWolbachia.VECTOR_WOLBACHIA_FREE

        released_genome (list[list[str]], optional):
            The alleles of the genome of the female vectors to be released. Each inner list
            defines one allele pair. Must define all alleles including the gender gene. Wildcards
            ('*') are not allowed.
            Default value: None

        released_mate_genome (list[list[str]], optional):
            The alleles of the genome of the male vectors that will mate with released females.
            When defined, released females will be fully gestated and ready to lay eggs.
            Default value: None

        released_microsporidia_strain (str, optional):
            The name of the microsporidia strain carried by the released mosquitoes. An empty
            string indicates no microsporidia.
            Default value: None

        common_intervention_parameters (CommonInterventionParameters, optional):
            The CommonInterventionParameters object that contains the 5 common
            parameters: cost, intervention_name, new_property_value, disqualifying_properties,
            dont_allow_duplicates.
            Default value: None
    """

    def __init__(self,
                 campaign: api_campaign,
                 released_species: str,
                 released_number: int = 10000,
                 released_ratio: float = 0.1,
                 released_type: ReleasedType = ReleasedType.FIXED_NUMBER,
                 released_infectious: float = 0,
                 released_wolbachia: ReleasedWolbachia = ReleasedWolbachia.VECTOR_WOLBACHIA_FREE,
                 released_genome: list[list[str]] = None,
                 released_mate_genome: list[list[str]] = None,
                 released_microsporidia_strain: str = None,
                 common_intervention_parameters: CommonInterventionParameters = None):
        super().__init__(campaign, 'MosquitoRelease', common_intervention_parameters)

        if not released_species:
            raise ValueError("'released_species' must be a non-empty string.")
        self._intervention.Released_Species = released_species
        self._intervention.Released_Type = str(released_type)
        self._intervention.Released_Number = validate_value_range(released_number, 'released_number', 1, 100000000, int)
        self._intervention.Released_Ratio = validate_value_range(released_ratio, 'released_ratio', 0, 3.40282e+38, float)
        self._intervention.Released_Infectious = validate_value_range(released_infectious, 'released_infectious', 0, 1, float)
        self._intervention.Released_Wolbachia = str(released_wolbachia)

        if released_genome is not None:
            self._intervention.Released_Genome = released_genome
        if released_mate_genome is not None:
            self._intervention.Released_Mate_Genome = released_mate_genome
        if released_microsporidia_strain is not None:
            self._intervention.Released_Microsporidia_Strain = released_microsporidia_strain


class MultiInsecticideIndoorSpaceSpraying(NodeIntervention):
    """
    The **MultiInsecticideIndoorSpaceSpraying** node intervention class applies indoor space
    spraying using multiple insecticides, each with their own killing waning effect.

    Args:
        campaign (api_campaign, required):
            An instance of the emod_api.campaign module.

        insecticides (list[InsecticideWaningEffectK], required):
            A list of per-insecticide killing waning effect definitions. Each element must be an
            **InsecticideWaningEffectK** instance.

        spray_coverage (float, optional):
            The proportion of the node that has been sprayed. This value is multiplied by the
            current efficacy of the waning effects.
            Minimum value: 0
            Maximum value: 1
            Default value: 1

        common_intervention_parameters (CommonInterventionParameters, optional):
            The CommonInterventionParameters object that contains the 5 common
            parameters: cost, intervention_name, new_property_value, disqualifying_properties,
            dont_allow_duplicates.
            Default value: None
    """

    def __init__(self,
                 campaign: api_campaign,
                 insecticides: list[InsecticideWaningEffectK],
                 spray_coverage: float = 1,
                 common_intervention_parameters: CommonInterventionParameters = None):
        super().__init__(campaign, 'MultiInsecticideIndoorSpaceSpraying', common_intervention_parameters)

        if not insecticides:
            raise ValueError("'insecticides' must be a non-empty list of InsecticideWaningEffectK instances.")
        for i, ins in enumerate(insecticides):
            if not isinstance(ins, InsecticideWaningEffectK):
                raise ValueError(f"'insecticides[{i}]' must be an instance of InsecticideWaningEffectK, not {type(ins)}.")

        self._intervention.Insecticides = [ins.to_schema_dict(campaign) for ins in insecticides]
        self._intervention.Spray_Coverage = validate_value_range(spray_coverage, 'spray_coverage', 0, 1, float)


class MultiInsecticideSpaceSpraying(NodeIntervention):
    """
    The **MultiInsecticideSpaceSpraying** node intervention class applies outdoor space spraying
    using multiple insecticides, each with their own killing waning effect.

    Args:
        campaign (api_campaign, required):
            An instance of the emod_api.campaign module.

        insecticides (list[InsecticideWaningEffectK], required):
            A list of per-insecticide killing waning effect definitions. Each element must be an
            **InsecticideWaningEffectK** instance.

        spray_coverage (float, optional):
            The proportion of the node that has been sprayed. This value is multiplied by the
            current efficacy of the waning effects.
            Minimum value: 0
            Maximum value: 1
            Default value: 1

        common_intervention_parameters (CommonInterventionParameters, optional):
            The CommonInterventionParameters object that contains the 5 common
            parameters: cost, intervention_name, new_property_value, disqualifying_properties,
            dont_allow_duplicates.
            Default value: None
    """

    def __init__(self,
                 campaign: api_campaign,
                 insecticides: list[InsecticideWaningEffectK],
                 spray_coverage: float = 1,
                 common_intervention_parameters: CommonInterventionParameters = None):
        super().__init__(campaign, 'MultiInsecticideSpaceSpraying', common_intervention_parameters)

        if not insecticides:
            raise ValueError("'insecticides' must be a non-empty list of InsecticideWaningEffectK instances.")
        for i, ins in enumerate(insecticides):
            if not isinstance(ins, InsecticideWaningEffectK):
                raise ValueError(f"'insecticides[{i}]' must be an instance of InsecticideWaningEffectK, not {type(ins)}.")

        self._intervention.Insecticides = [ins.to_schema_dict(campaign) for ins in insecticides]
        self._intervention.Spray_Coverage = validate_value_range(spray_coverage, 'spray_coverage', 0, 1, float)


class OutdoorNodeEmanator(NodeIntervention):
    """
    The **OutdoorNodeEmanator** node intervention class places an emanating device outdoors in the
    node that repels and/or kills vectors in the outdoor environment.

    Args:
        campaign (api_campaign, required):
            An instance of the emod_api.campaign module.

        killing_config (AbstractWaningConfig, required):
            The configuration of killing efficacy of the intervention. Specify how this effect
            decays over time using one of the Waning Config classes in
            emodpy_hiv.campaign.waning_config.

        repelling_config (AbstractWaningConfig, required):
            The configuration of repelling efficacy of the intervention. A vector is repelled
            before any killing can occur. Specify how this effect decays over time using one of
            the Waning Config classes in emodpy_hiv.campaign.waning_config.

        spray_coverage (float, optional):
            The proportion of the node covered by this intervention. This value is multiplied
            by the current efficacy of the waning effects.
            Minimum value: 0
            Maximum value: 1
            Default value: 1

        insecticide_name (str, optional):
            The name of the insecticide defined in the configuration parameter **Insecticides**
            for this intervention. If insecticides are not being used, this can be left empty.
            Default value: None

        common_intervention_parameters (CommonInterventionParameters, optional):
            The CommonInterventionParameters object that contains the 5 common
            parameters: cost, intervention_name, new_property_value, disqualifying_properties,
            dont_allow_duplicates.
            Default value: None
    """

    def __init__(self,
                 campaign: api_campaign,
                 killing_config: AbstractWaningConfig,
                 repelling_config: AbstractWaningConfig,
                 spray_coverage: float = 1,
                 insecticide_name: str = None,
                 common_intervention_parameters: CommonInterventionParameters = None):
        super().__init__(campaign, 'OutdoorNodeEmanator', common_intervention_parameters)

        for param_name, waning in [('killing_config', killing_config),
                                   ('repelling_config', repelling_config)]:
            if not isinstance(waning, AbstractWaningConfig):
                raise ValueError(f"'{param_name}' must be an instance of AbstractWaningConfig, not {type(waning)}.")

        self._intervention.Killing_Config = killing_config.to_schema_dict(campaign)
        self._intervention.Repelling_Config = repelling_config.to_schema_dict(campaign)
        self._intervention.Spray_Coverage = validate_value_range(spray_coverage, 'spray_coverage', 0, 1, float)

        if insecticide_name is not None:
            self._intervention.Insecticide_Name = insecticide_name


class OutdoorRestKill(NodeIntervention):
    """
    The **OutdoorRestKill** node intervention class kills vectors that rest outdoors in the node,
    applying a configurable killing waning effect during the outdoor resting phase.

    Args:
        campaign (api_campaign, required):
            An instance of the emod_api.campaign module.

        killing_config (AbstractWaningConfig, required):
            The configuration of killing efficacy of the intervention. Specify how this effect
            decays over time using one of the Waning Config classes in
            emodpy_hiv.campaign.waning_config.

        insecticide_name (str, optional):
            The name of the insecticide defined in the configuration parameter **Insecticides**
            for this intervention. If insecticides are not being used, this can be left empty.
            Default value: None

        common_intervention_parameters (CommonInterventionParameters, optional):
            The CommonInterventionParameters object that contains the 5 common
            parameters: cost, intervention_name, new_property_value, disqualifying_properties,
            dont_allow_duplicates.
            Default value: None
    """

    def __init__(self,
                 campaign: api_campaign,
                 killing_config: AbstractWaningConfig,
                 insecticide_name: str = None,
                 common_intervention_parameters: CommonInterventionParameters = None):
        super().__init__(campaign, 'OutdoorRestKill', common_intervention_parameters)

        if not isinstance(killing_config, AbstractWaningConfig):
            raise ValueError(f"'killing_config' must be an instance of AbstractWaningConfig, not {type(killing_config)}.")
        self._intervention.Killing_Config = killing_config.to_schema_dict(campaign)

        if insecticide_name is not None:
            self._intervention.Insecticide_Name = insecticide_name


class OvipositionTrap(NodeIntervention):
    """
    The **OvipositionTrap** node intervention class places traps in larval habitats that kill
    female mosquitoes during oviposition cycles.

    Args:
        campaign (api_campaign, required):
            An instance of the emod_api.campaign module.

        killing_config (AbstractWaningConfig, required):
            The configuration of killing efficacy for the fraction of oviposition cycles that end
            in the female mosquito's death. Specify how this effect decays over time using one of
            the Waning Config classes in emodpy_hiv.campaign.waning_config.

        habitat_target (HabitatType, optional):
            The larval habitat type to place traps in. Possible values are:
            * NONE
            * TEMPORARY_RAINFALL
            * WATER_VEGETATION
            * HUMAN_POPULATION
            * CONSTANT
            * BRACKISH_SWAMP
            * LINEAR_SPLINE
            * ALL_HABITATS
            Default value: HabitatType.ALL_HABITATS

        common_intervention_parameters (CommonInterventionParameters, optional):
            The CommonInterventionParameters object that contains the 5 common
            parameters: cost, intervention_name, new_property_value, disqualifying_properties,
            dont_allow_duplicates.
            Default value: None
    """

    def __init__(self,
                 campaign: api_campaign,
                 killing_config: AbstractWaningConfig,
                 habitat_target: HabitatType = HabitatType.ALL_HABITATS,
                 common_intervention_parameters: CommonInterventionParameters = None):
        super().__init__(campaign, 'OvipositionTrap', common_intervention_parameters)

        if not isinstance(killing_config, AbstractWaningConfig):
            raise ValueError(f"'killing_config' must be an instance of AbstractWaningConfig, not {type(killing_config)}.")
        self._intervention.Killing_Config = killing_config.to_schema_dict(campaign)
        self._intervention.Habitat_Target = str(habitat_target)


class ScaleLarvalHabitat(NodeIntervention):
    """
    The **ScaleLarvalHabitat** node intervention class scales the availability of larval habitats
    in the node. It can target all habitats, specific habitat types, or specific mosquito species
    within each habitat type.

    Args:
        campaign (api_campaign, required):
            An instance of the emod_api.campaign module.

        larval_habitat_multiplier (list[LarvalHabitatMultiplierSpec], required):
            A list of **LarvalHabitatMultiplierSpec** objects defining how to scale larval habitat
            availability. Each entry can target a different habitat type and/or species.

        common_intervention_parameters (CommonInterventionParameters, optional):
            The CommonInterventionParameters object that contains the 4 common
            parameters: intervention_name, new_property_value, disqualifying_properties,
            dont_allow_duplicates.
            The following parameter is not valid for this intervention:
            cost
            Default value: None
    """

    def __init__(self,
                 campaign: api_campaign,
                 larval_habitat_multiplier: list[LarvalHabitatMultiplierSpec],
                 common_intervention_parameters: CommonInterventionParameters = None):
        super().__init__(campaign, 'ScaleLarvalHabitat', common_intervention_parameters)

        if not larval_habitat_multiplier:
            raise ValueError("'larval_habitat_multiplier' must be a non-empty list of LarvalHabitatMultiplierSpec instances.")
        for i, spec in enumerate(larval_habitat_multiplier):
            if not isinstance(spec, LarvalHabitatMultiplierSpec):
                raise ValueError(f"'larval_habitat_multiplier[{i}]' must be an instance of LarvalHabitatMultiplierSpec, not {type(spec)}.")

        self._intervention.Larval_Habitat_Multiplier = [spec.to_schema_dict(campaign) for spec in larval_habitat_multiplier]

    def _set_cost(self, cost: float) -> None:
        raise ValueError('Cost_To_Consumer is not a valid parameter for the ScaleLarvalHabitat intervention.')


class SpaceSpraying(NodeIntervention):
    """
    The **SpaceSpraying** node intervention class applies outdoor space spraying to kill
    mosquitoes in the node. The proportion of the node sprayed is controlled by
    **spray_coverage**.

    Args:
        campaign (api_campaign, required):
            An instance of the emod_api.campaign module.

        killing_config (AbstractWaningConfig, required):
            The configuration of killing efficacy of the intervention. Specify how this effect
            decays over time using one of the Waning Config classes in
            emodpy_hiv.campaign.waning_config.

        spray_coverage (float, optional):
            The proportion of the node that has been sprayed. This value is multiplied by the
            current efficacy of the waning effect.
            Minimum value: 0
            Maximum value: 1
            Default value: 1

        insecticide_name (str, optional):
            The name of the insecticide defined in the configuration parameter **Insecticides**
            for this intervention. If insecticides are not being used, this can be left empty.
            Default value: None

        common_intervention_parameters (CommonInterventionParameters, optional):
            The CommonInterventionParameters object that contains the 5 common
            parameters: cost, intervention_name, new_property_value, disqualifying_properties,
            dont_allow_duplicates.
            Default value: None
    """

    def __init__(self,
                 campaign: api_campaign,
                 killing_config: AbstractWaningConfig,
                 spray_coverage: float = 1,
                 insecticide_name: str = None,
                 common_intervention_parameters: CommonInterventionParameters = None):
        super().__init__(campaign, 'SpaceSpraying', common_intervention_parameters)

        if not isinstance(killing_config, AbstractWaningConfig):
            raise ValueError(f"'killing_config' must be an instance of AbstractWaningConfig, not {type(killing_config)}.")
        self._intervention.Killing_Config = killing_config.to_schema_dict(campaign)
        self._intervention.Spray_Coverage = validate_value_range(spray_coverage, 'spray_coverage', 0, 1, float)

        if insecticide_name is not None:
            self._intervention.Insecticide_Name = insecticide_name


class SpatialRepellent(NodeIntervention):
    """
    The **SpatialRepellent** node intervention class places a spatial repellent device in the node
    that repels vectors before they can feed on humans.

    Args:
        campaign (api_campaign, required):
            An instance of the emod_api.campaign module.

        repelling_config (AbstractWaningConfig, required):
            The configuration of repelling efficacy of the intervention. A vector is repelled
            before any blocking or killing can occur. Specify how this effect decays over time
            using one of the Waning Config classes in emodpy_hiv.campaign.waning_config.

        spray_coverage (float, optional):
            The proportion of the node covered by this intervention. This value is multiplied
            by the current efficacy of the waning effect.
            Minimum value: 0
            Maximum value: 1
            Default value: 1

        insecticide_name (str, optional):
            The name of the insecticide defined in the configuration parameter **Insecticides**
            for this intervention. If insecticides are not being used, this can be left empty.
            Default value: None

        common_intervention_parameters (CommonInterventionParameters, optional):
            The CommonInterventionParameters object that contains the 5 common
            parameters: cost, intervention_name, new_property_value, disqualifying_properties,
            dont_allow_duplicates.
            Default value: None
    """

    def __init__(self,
                 campaign: api_campaign,
                 repelling_config: AbstractWaningConfig,
                 spray_coverage: float = 1,
                 insecticide_name: str = None,
                 common_intervention_parameters: CommonInterventionParameters = None):
        super().__init__(campaign, 'SpatialRepellent', common_intervention_parameters)

        if not isinstance(repelling_config, AbstractWaningConfig):
            raise ValueError(f"'repelling_config' must be an instance of AbstractWaningConfig, not {type(repelling_config)}.")
        self._intervention.Repelling_Config = repelling_config.to_schema_dict(campaign)
        self._intervention.Spray_Coverage = validate_value_range(spray_coverage, 'spray_coverage', 0, 1, float)

        if insecticide_name is not None:
            self._intervention.Insecticide_Name = insecticide_name


class SugarTrap(NodeIntervention):
    """
    The **SugarTrap** node intervention class places sugar-bait traps in the node that attract
    and kill mosquitoes seeking sugar meals. Traps can have a configurable expiration period.

    Args:
        campaign (api_campaign, required):
            An instance of the emod_api.campaign module.

        killing_config (AbstractWaningConfig, required):
            The configuration of killing efficacy of the intervention. Specify how this effect
            decays over time using one of the Waning Config classes in
            emodpy_hiv.campaign.waning_config.

        expiration_period_distribution (BaseDistribution, optional):
            The distribution type to use for the trap expiration period. Each trap instance gets
            an expiration duration drawn from this distribution. Please use one of the following
            distribution classes from emodpy_hiv.utils.distributions:
            * ConstantDistribution
            * UniformDistribution
            * GaussianDistribution
            * ExponentialDistribution
            * PoissonDistribution
            * LogNormalDistribution
            * DualConstantDistribution
            * WeibullDistribution
            * DualExponentialDistribution
            If not provided, the trap does not expire (NOT_INITIALIZED).
            Default value: None

        insecticide_name (str, optional):
            The name of the insecticide defined in the configuration parameter **Insecticides**
            for this intervention. If insecticides are not being used, this can be left empty.
            Default value: None

        common_intervention_parameters (CommonInterventionParameters, optional):
            The CommonInterventionParameters object that contains the 5 common
            parameters: cost, intervention_name, new_property_value, disqualifying_properties,
            dont_allow_duplicates.
            Default value: None
    """

    def __init__(self,
                 campaign: api_campaign,
                 killing_config: AbstractWaningConfig,
                 expiration_period_distribution: BaseDistribution = None,
                 insecticide_name: str = None,
                 common_intervention_parameters: CommonInterventionParameters = None):
        super().__init__(campaign, 'SugarTrap', common_intervention_parameters)

        if not isinstance(killing_config, AbstractWaningConfig):
            raise ValueError(f"'killing_config' must be an instance of AbstractWaningConfig, not {type(killing_config)}.")
        self._intervention.Killing_Config = killing_config.to_schema_dict(campaign)

        if expiration_period_distribution is not None:
            if not isinstance(expiration_period_distribution, BaseDistribution):
                raise ValueError(f"'expiration_period_distribution' must be an instance of BaseDistribution, not {type(expiration_period_distribution)}.")
            self.set_distribution(expiration_period_distribution, 'Expiration_Period')

        if insecticide_name is not None:
            self._intervention.Insecticide_Name = insecticide_name


# __all_exports: A list of classes that are intended to be exported from this module.
__all_exports = [
    ArtificialDietTarget,
    EIRType,
    HabitatType,
    MalariaChallengeType,
    ReleasedType,
    ReleasedWolbachia,
    InsecticideWaningEffectK,
    LarvalHabitatMultiplierSpec,
    AnimalFeedKill,
    ArtificialDiet,
    IndoorSpaceSpraying,
    InputEIR,
    LarvalMicrosporidiaIntervention,
    Larvicides,
    MalariaChallenge,
    MosquitoRelease,
    MultiInsecticideIndoorSpaceSpraying,
    MultiInsecticideSpaceSpraying,
    OutdoorNodeEmanator,
    OutdoorRestKill,
    OvipositionTrap,
    ScaleLarvalHabitat,
    SpaceSpraying,
    SpatialRepellent,
    SugarTrap,
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
