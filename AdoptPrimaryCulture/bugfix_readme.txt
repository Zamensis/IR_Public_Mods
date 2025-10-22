Hello myself, or fellow modder.

This mod contains an effect, "z_apc_set_primary_culture_effect", that requires a bit of an explanation.
I make this not in case I forget everything, or someone else is curious about it.

There's an annoying bug in the base game (and Invictus at the time of writing this):

When using the "set_primary_culture" or "set_primary_culture_cleanup_effect", the game fails to fetch the correct the number of integrated/noble cultures, resulting in a "ghost" malus for the new primary culture.

After much efforts, I was able to fix it in one game-tick so the player barely notices it.

Here's how it works, in English. For more technical details, read the workflow and comments in "z_apc_set_primary_culture_effect".

	0) Immediately after using "set_primary_culture" or "set_primary_culture_cleanup_effect"...
	
	1) Convert all pops from the original primary culture to another culture, that isn't already present in the country (so they can be easily scoped to in step 4).
	
	2) Give the country a random province in the world with pops of yet another culture that isn't already present in the country. Make sure the original owner is neither a player (that would annoy him), an OPM (that would destroy him) or at war (that could affect the outcome). Maybe choose a province with very few pops as to minimize the risk of erasing a non-permanent province modifier. This change of ownership seems to force an update of the country cultures list.
	
	3) Immediately give that province back to its original owner.
	
	4) Convert all the formerly primary pops back to the old primary culture.
	
	5) Do the province trick again, to force another update of the country cultures.
	
	6) The correct number of integrated/noble cultures will be calculated on the next monthly tick. The job is done! Well, almost...
	
	7) The old primary culture is considered freemen, regardless of the player decision to keep it integrated or not. So if the intent was to keep them integrated, it needs to be done manually.
	
That is all.