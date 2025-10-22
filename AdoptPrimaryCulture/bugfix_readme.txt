Hello myself, or fellow modder.

This mod contains an effect, "z_apc_set_primary_culture_effect", that requires a bit of an explanation.
I make this not in case I forget everything, or someone else is curious about it.

There's an annoying bug in the base game (and Invictus at the time of writing this):

When using the "set_primary_culture" or "set_primary_culture_cleanup_effect", the game fails to fetch the correct the number of integrated/noble cultures, resulting in a "ghost" malus for the new primary culture.

After much efforts, I was able to fix it in one game-tick so the player barely notices it.

Here's how it works, in English. For more technical details, read the workflow and comments in "z_apc_set_primary_culture_effect".

	0) Save the necessary scopes for the old primary culture, the new one, and a temporary one that isn't already present in the country (so it can be easily scoped to).

	1) Use the "set_primary_culture" or "set_primary_culture_cleanup_effect" as usual.
	
	2) Store the MAKE_OLD_CULTURE_INTEGRATED parameter in a separate variable (because the fix will force the old culture back to the "freemen" type, so it will have to be reintegrated manually if necessary).
	
	3) Convert all pops from the original primary culture to the temporary one.
	
	4) Give the country a random province in the world with pops of yet another culture that isn't already present in the country. This change of ownership forces an update of the country cultures list. Then immediately give that province back to its original owner.
	
	5) Convert all the formerly primary pops (currently in the temporary culture) back to the old primary culture.
	
	6) Do the province trick again, to force another update of the country cultures.
	
	7) The correct number of integrated/noble cultures will be calculated on the next monthly tick. The job is almost done! The old primary culture is considered freemen, regardless of the player decision to keep it integrated or not. So if the intent was to keep them integrated, it needs to be done manually.
	
That is all.