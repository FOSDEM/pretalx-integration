with managers as
((select ts.mail, email FROM submission_track t
join devroom_settings_tracksettings ts on t.id=ts.track_id
join event_teaminvite et on et.team_id=ts.manager_team_id
where ts.track_type='D')
union all
(select ts.mail,  email FROM submission_track t
join devroom_settings_tracksettings ts on t.id=ts.track_id
join event_team_members em on em.team_id=ts.manager_team_id
join person_user u on em.user_id=u.id
where ts.track_type='D'
))
select distinct email from managers order by email;

