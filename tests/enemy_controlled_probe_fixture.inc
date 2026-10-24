/* Test-only bridge appended to a copy of game_probe.c. Never compiled into the
 * game binary: fixtures exercise the exact private contract functions; they
 * are NOT evidence of original-event reachability or legal startup. */
void enemy_controlled_probe_fixture_start(void)
{
 probe_requested=true;game_probe_enabled=asset_debug_enabled=true;play_demo=true;record_demo=stopped_demo=false;
 loadout_selected=sidekicks_selected=charge_stages=fade_cycle_scene=banking_scene=enemy_hit_scene=false;
 preview_port[0]=1;preview_port[1]=0;preview_power[0]=preview_power[1]=preview_rear_mode=1;
 probe_start_contract();probe_level_contract();
}
void enemy_controlled_probe_fixture_profile_change(void) {enemy_hit_scene=!enemy_hit_scene;}
