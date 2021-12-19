import PySimpleGUI as sg


def settings_window_layout():
    # Track drawing attributes
    tracks_marks = sg.Checkbox(
        "marks",
        key="track.marks",
        enable_events=True,
        default=True,
    )
    tracks_fill = sg.Checkbox(
        "fill",
        key="track.fill",
        enable_events=True,
        default=True,
    )
    tracks_grid = sg.Checkbox(
        "grid",
        key="track.grid",
        enable_events=True,
        default=False,
    )
    tracks_splines = sg.Checkbox(
        "splines",
        key="track.splines",
        enable_events=True,
        default=False,
    )
    tracks_alpha_text = sg.Text("Transparency: ")
    tracks_alpha_slider = sg.Slider(
        range=(0, 1),
        resolution=0.1,
        default_value=0.5,
        orientation="h",
        expand_x=True,
        key="track.transparency",
        enable_events=True,
    )
    track_draw_layout = [
        [
            sg.Column([[tracks_marks], [tracks_fill]]),
            sg.Column([[tracks_grid], [tracks_splines]]),
        ],
        [tracks_alpha_text],
        [tracks_alpha_slider],
    ]
    track_draw_frame = sg.Frame(
        "Track drawing",
        layout=track_draw_layout,
        expand_x=True,
        expand_y=True,
    )

    # Track label attribute
    track_new = sg.Button(
        "New Track",
        enable_events=True,
        key="track.new",
        expand_x=True,
    )
    track_delete = sg.Button(
        "Del Track",
        enable_events=True,
        key="track.del",
        expand_x=True,
        button_color="red",
    )
    track_active_text = sg.Text("Active track:")
    track_active_list = sg.Listbox(
        values=[],
        expand_x=True,
        size=(0, 5),
        enable_events=True,
        key="track.active.track",
        select_mode=sg.LISTBOX_SELECT_MODE_SINGLE,
    )
    track_relpos_left = sg.Radio(
        "left",
        key="track.relpos.left",
        group_id="track.relpos",
        enable_events=True,
        expand_x=True,
    )
    track_relpos_ego = sg.Radio(
        "ego",
        key="track.relpos.ego",
        group_id="track.relpos",
        enable_events=True,
        expand_x=True,
    )
    track_relpos_right = sg.Radio(
        "right",
        key="track.relpos.right",
        group_id="track.relpos",
        enable_events=True,
        expand_x=True,
    )
    track_relpos = [track_relpos_left, track_relpos_ego, track_relpos_right]
    track_label_layout = [
        track_relpos,
        [track_new, track_delete],
        [track_active_text],
        [track_active_list],
    ]
    track_label_frame = sg.Frame(
        "Track label",
        layout=track_label_layout,
        expand_x=True,
        expand_y=True,
    )

    # Switch drawing attributes
    switch_marks = sg.Checkbox(
        "marks", key="switches.marks", enable_events=True, default=True
    )
    switch_fill = sg.Checkbox(
        "fill", key="switches.fill", enable_events=True, default=True
    )
    switch_alpha_text = sg.Text("Transparency: ")
    switch_alpha_slider = sg.Slider(
        range=(0, 1),
        resolution=0.1,
        default_value=0.5,
        orientation="h",
        expand_x=True,
        key="switches.alpha",
        enable_events=True,
    )
    switch_layout = [
        [switch_marks, switch_fill],
        [switch_alpha_text],
        [switch_alpha_slider],
    ]
    switch_draw_frame = sg.Frame(
        "Switch drawing",
        layout=switch_layout,
        expand_x=True,
        expand_y=True,
    )

    # Switch label attribute
    switch_new = sg.Button(
        "New Switch",
        enable_events=True,
        key="switch.new",
        expand_x=True,
    )
    switch_delete = sg.Button(
        "Del Switch",
        enable_events=True,
        key="switch.del",
        expand_x=True,
        button_color="red",
    )
    switch_active_text = sg.Text("Active switch:")
    switch_active_list = sg.Listbox(
        values=[],
        expand_x=True,
        size=(0, 5),
        enable_events=True,
        key="switch.active.switch",
        select_mode=sg.LISTBOX_SELECT_MODE_SINGLE,
    )
    switch_kind_forg = sg.Radio(
        "Fork",
        key="switch.kind.fork",
        group_id="switch.kind",
        enable_events=True,
        expand_x=True,
    )
    switch_kind_merge = sg.Radio(
        "Merge",
        key="switch.kind.merge",
        group_id="switch.kind",
        enable_events=True,
        expand_x=True,
    )
    switch_kind = sg.Column(
        [[switch_kind_forg], [switch_kind_merge]],
        expand_x=True,
    )
    switch_direction_right = sg.Radio(
        "Right",
        key="switch.direction.right",
        group_id="switch.direction",
        enable_events=True,
        expand_x=True,
    )
    switch_direction_left = sg.Radio(
        "Left",
        key="switch.direction.left",
        group_id="switch.direction",
        enable_events=True,
        expand_x=True,
    )
    switch_direction = sg.Column(
        [[switch_direction_right], [switch_direction_left]], expand_x=True
    )
    switch_label_layout = [
        [
            switch_kind,
            sg.VerticalSeparator(),
            switch_direction,
        ],
        [switch_new, switch_delete],
        [switch_active_text],
        [switch_active_list],
    ]
    switch_label_frame = sg.Frame(
        "Switch label",
        layout=switch_label_layout,
        expand_x=True,
    )

    # Tags
    scene_tags_list = sg.Listbox(
        values=[],
        expand_x=True,
        size=(0, 5),
        enable_events=True,
        key="scene.tags",
        select_mode=sg.LISTBOX_SELECT_MODE_MULTIPLE,
        expand_y=True,
    )
    scene_tags_frame = sg.Frame(
        "Scene Tags",
        layout=[[scene_tags_list]],
        expand_x=True,
        expand_y=True,
    )

    # Tabs
    label_tabs = sg.TabGroup(
        [
            [
                sg.Tab(
                    "Track", [[track_draw_frame, track_label_frame]], key="track.tab"
                ),
                sg.Tab(
                    "Switch",
                    [[sg.Column([[switch_draw_frame, switch_label_frame]])]],
                    key="switch.tab",
                ),
            ],
        ],
        key="mode.tab",
        enable_events=True,
    )

    tabs_and_tags_column = sg.Column([[label_tabs, scene_tags_frame]])

    # Window layout
    layout = [
        [tabs_and_tags_column],
        [
            sg.Button("Previous"),
            sg.Text("xxx of xxx", key="scene.counter"),
            sg.Button("Next"),
            sg.Button("Exit", button_color="red"),
            sg.Text("Scene name", key="scene.name"),
        ],
    ]
    return layout
