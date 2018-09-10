
import numpy as np
import glob
import os
import json
import logging
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
import flask
from guesswho import *


logging.basicConfig(level=logging.INFO)

LANG = 'nl'

game = GuessWhoGame(data_file='./data/test.json')

# characters = [
#     {'name': os.path.splitext(os.path.basename(filename))[0].split('-')[0],
#      'file': filename
#      } for filename in glob.glob('./images/*.jpg')
# ]
characters = game.get_characters()
questions = game.PROPERTIES
initial_hidden_state = json.dumps({c['id']: True for c in characters})
default_image = '/images/game/unknown.jpg'

TEXT_EN = {
    'hair color': 'Hair color',
    'dark': 'dark', 'light': 'light', 'none': 'none',
    'hair length': 'Hair length',
    'short': 'short', 'long': 'long', 'bald': 'bald',
    'hair type': 'Hair type',
    'curly': 'curly', 'straight': 'straight',
    'glasses': 'Glasses',
    'yes': 'yes', 'no': 'no',
    'head wear': 'Head wear',
    'hat': 'hat', 'cap': 'cap',
    'sex': 'Gender',
    'male': 'man', 'female': 'woman',
    'facial hair': 'Facial hair',
    'beard': 'beard', 'moustache': 'moustache',
    'accessories': 'Accessories',
    'chain': 'chain', 'necklace': 'necklace',
    'player_computer': 'Computer',
    'player_human': 'You',
    'select_difficulty': 'Select computer difficulty',
    'level_hard': 'Hard',
    'level_easy': 'Easy',
    'select_character': 'Select computer character',
    'select_question': 'Select your next question:',
    'category': 'Category:',
    'options': 'Options:',
    'ask': 'Ask!',
    'guess': 'Guess!',
    'answer': 'Answer',
    'end_turn': 'End turn',
    'end_game': 'End game',
    'waiting_for_computer': 'Waiting for computer to move...',
    'welcome_header': 'Welcome! To play a game:',
    'welcome_bullet1': 'Start a new game',
    'welcome_bullet2': 'Select a character that the computer needs to guess',
    'welcome_bullet3': 'Select a question, or make a guess if you\'re feeling confident',
    'welcome_bullet4': 'Click "End turn" and wait for the computer to move',
    'start_game': 'Start the game!',
    'already_moved': 'You\'ve already made a move. Click "End turn".',
    'not': 'not',
    'make_a_guess': '...or make a guess!',
    'pick_a_character': 'Pick a character'

}

TEXT_NL = {
    'hair color': 'Haarkleur',
    'dark': 'donker', 'light': 'licht', 'none': 'geen',
    'hair length': 'Haarlengte',
    'short': 'kort', 'long': 'lang', 'bald': 'kaal',
    'hair type': 'Haartype',
    'curly': 'krullend', 'straight': 'steil',
    'glasses': 'Bril',
    'yes': 'ja', 'no': 'nee',
    'head wear': 'Hoofddeksel',
    'hat': 'hoed', 'cap': 'pet',
    'sex': 'Geslacht',
    'male': 'man', 'female': 'vrouw',
    'facial hair': 'Gezichtsbeharing',
    'beard': 'baard', 'moustache': 'snor',
    'accessories': 'Accessoires',
    'chain': 'kettinkje', 'necklace': 'ketting',
    'player_computer': 'Computer',
    'player_human': 'Jij',
    'select_difficulty': 'Selecteer moeilijkheidsgraad',
    'level_hard': 'Moeilijk',
    'level_easy': 'Gemakkelijk',
    'select_character': 'Selecteer karakter voor de computer',
    'select_question': 'Kies je volgende vraag:',
    'category': 'Categorie:',
    'options': 'Opties:',
    'ask': 'Vraag!',
    'guess': 'Raad!',
    'answer': 'Antwoord',
    'end_turn': 'Einde beurt',
    'end_game': 'Spel afsluiten',
    'waiting_for_computer': 'Wachten op de beurt van de computer...',
    'welcome_header': 'Welkom! Het spel werkt als volgt:',
    'welcome_bullet1': 'Start het spel',
    'welcome_bullet2': 'Kies eerst een karakter voor de comouter om te raden',
    'welcome_bullet3': 'Selecteer een vraag, of doe een gokje. Flip zelf de afgevallen karakters weg',
    'welcome_bullet4': 'Klik op "Einde beurt" en wacht op de beurt van de computer',
    'start_game': 'Start het spel!',
    'already_moved': 'Je hebt al een vraag gesteld. Klik op "Einde beurt".',
    'not': 'niet',
    'make_a_guess': '...of waag een gokje!',
    'pick_a_character': 'Kies een karakter'
}

if LANG == 'nl':
    TEXT = TEXT_NL
    GAME_LOGO = 'wie-is-het-logo.jpg'
    #GAME_LOGO = 'wie-is-het-logo-2.png'
else:
    TEXT = TEXT_EN
    GAME_LOGO = 'guesswho_logo.png'


def create_test_data(out_file):
    idx = 0
    data = []
    for c in characters:
        idx += 1
        x = c
        x['id'] = idx
        x['properties'] = {}
        for k, v in questions.items():
            choice = np.random.randint(0, len(v))
            x['properties'][k] = v[choice]
        data.append(x)
    with open(out_file, 'w') as f:
        json.dump(data, f)


#create_test_data('./guesswho/data/test.json')

def reset_game():
    global game
    global characters
    global questions
    
    game = GuessWhoGame(data_file='./data/test.json')
    characters = game.get_characters()
    questions = game.PROPERTIES


def get_character_options():
    return [{'label': c['name'], 'value': c['name']} for c in game.board.get_characters()]


def get_question_type_options():
    return [{'label': TEXT[x], 'value': x} for x in questions.keys()]


def get_question_value_options(question_type):
    return [{'label': TEXT[x], 'value': x} for x in questions[question_type]]


def get_answer(question_type, question_value):
    ok = question_type is not None and question_value is not None
    if not ok:
        return False, False

    ok, answer = game.human_player.ask_question((question_type, question_value))
    return ok, answer


def guess_character(name):
    character = game.board.get_character_by_name(name)
    ok, answer = game.human_player.guess_character(character)
    return ok, answer


def render_board_characters(player_id):
    elements = []
    for c in characters:
        elements.append(
            html.A(
                id='a-p{}-character-{}'.format(player_id, c['id']),
                href="javascript:clickCharacter({}, {})".format(player_id, c['id']),
                n_clicks=0,
                children=[
                    html.Figure(className='character-container has-text-centered', children=[
                        html.Img(id='img-p{}-character-{}'.format(player_id, c['id']), className='character-image', src=c['file']),
                        html.Figcaption(className='character-caption', children=c['name'])
                    ])
                ]
            )
        )
    return elements


def bulma_center(component):
    return html.Div(className='columns', children=[
        html.Div(className='column', children=[]),
        html.Div(className='column has-text-centered', children=[component]),
        html.Div(className='column', children=[])
    ])


def bulma_columns(components):
    return html.Div(className='columns has-text-centered', children=[
        html.Div(className='column', children=[c]) for c in components
    ])


def bulma_field(label, component):
    """
    Handle boiler plate stuff for putting a label on a dcc / input field
    """
    return html.Div(className='field', children=[
        html.Label(className='label', children=label),
        html.Div(className='control', children=[component])
    ])


def bulma_modal(id, content=None, btn_text='OK', btn_class='is-info', active=False):
    """
    Create a modal (overlay) in bulma format
    """
    return html.Div(className='modal {}'.format('is-active' if active else ''), id='{}-modal'.format(id), children=[
        html.Div(className='modal-background'),
        html.Div(className='modal-content', children=[
            html.Div(className='box', children=[
                html.Div(className='content', children=[
                    html.Div(id='{}-modal-content'.format(id), children=content),
                    html.Button(id='{}-modal-button'.format(id),
                                className='button is-medium {}'.format(btn_class),
                                n_clicks=0,
                                children=btn_text
                                )
                ])
            ])
        ])
    ])


app = dash.Dash()

app.layout = html.Div(children=[
    bulma_columns([
        html.Img(className='header-logo', src='/images/game/{}'.format(GAME_LOGO)),
        '',
        html.Img(className='header-logo', src='/images/game/Logo_datasciencelab.png')
    ]),

    # Computer player board
    html.Div(className='character-board panel', children=[
        html.P(className="panel-heading", children=TEXT['player_computer']),
        html.Div(className="panel-block is-block", children=[
            html.Div(id="computer-board", children=render_board_characters(player_id=1)),
            html.Progress(id='computer-progress', className="progress is-info", value="0", max="100"),
            html.Div(id='output-hidden-state', accessKey=initial_hidden_state)
        ])
    ]),

    # Select computer difficulty and character
    bulma_center(
        html.Div(id='computer-character', className='level', children=[
            html.Div(className='level-left', children=[
                html.Div(className='level-item', children=[
                    bulma_field(label=TEXT['select_difficulty'],
                                component=dcc.Dropdown(id='input-computer-mode',
                                                       options=[{'label': TEXT['level_hard'], 'value': 'hard'},
                                                                {'label': TEXT['level_easy'], 'value': 'easy'}],
                                                       value='hard'
                                                       )
                                )
                ]),
                html.Div(className='level-item', children=[
                    bulma_field(label=TEXT['select_character'],
                                component=dcc.Dropdown(id='input-character-select', options=get_character_options())
                                )
                ]),
                html.Div(className='level-item', children=[
                    html.Img(id='output-selected-character', src=default_image)
                ])
            ]),
            html.Div(className='level-right', children=[])
        ])
    ),
    dcc.Input(id='output-dummy-1', type='hidden', className='is-hidden', value=''),
    dcc.Input(id='output-dummy-2', type='hidden', className='is-hidden', value=''),

    # Human player board
    html.Div(className='character-board panel', children=[
        html.P(id="player-name", className="panel-heading", children=TEXT['player_human']),
        html.Div(className="panel-block is-block", children=[
            html.Div(id='player-board', children=render_board_characters(player_id=2)),
            html.Progress(id='player-progress', className="progress is-danger", value="0", max="100"),
            html.Div(className='columns', children=[
                html.Div(className='column', children=[
                    html.H4(TEXT['select_question'])
                ]),
                html.Div(className='column', children=[
                    bulma_field(label=TEXT['category'],
                                component=dcc.Dropdown(id='input-question-type',
                                                       options=get_question_type_options())
                                )
                ]),
                html.Div(className='column', children=[
                    bulma_field(TEXT['options'], dcc.Dropdown(id='input-question-value', options=[], multi=False))
                ]),
                html.Div(className='column', children=[
                    bulma_field(label=[html.Span(className='is-invisible', children='.')],
                                component=html.Button(id='input-question-button',
                                                      className='button is-info is-inverted',
                                                      n_clicks=0,
                                                      children=TEXT['ask']
                                                      )
                                )
                ])
            ]),
            html.Div(className='columns', children=[
                html.Div(className='column', children=[
                    html.H4(TEXT['make_a_guess'])
                ]),
                html.Div(className='column is-half', children=[
                    bulma_field(label=TEXT['pick_a_character'],
                                component=dcc.Dropdown(id='input-character-guess',
                                                       options=get_character_options(),
                                                       multi=False
                                                       )
                                )
                ]),
                html.Div(className='column', children=[
                    bulma_field(label=[html.Span(className='is-invisible', children='.')],
                                component=html.Button(id='input-guess-button',
                                                      className='button is-info is-inverted',
                                                      n_clicks=0,
                                                      children=TEXT['guess']
                                                      )
                                )
                ])
            ]),
            html.Div([
                bulma_field(label=TEXT['answer'], component=html.Div(id='output-question-answer', children=''))
            ]),
            html.Div(id='output-hidden-guess', accessKey="")
        ])
    ]),

    # Bottom part
    bulma_center(
        html.Button(id='input-endturn-button', className='button is-info is-large', n_clicks=0, children=TEXT['end_turn'])
    ),

    html.Div(className='modal', id='end-modal', children=[
        html.Div(className='modal-background'),
        html.Div(className='modal-content', children=[
            html.Div(className='box', children=[
                html.Div(className='content', children=[
                    html.Div(id='end-modal-content', children=''),
                    html.Button(id='end-modal-button', className='button is-large', n_clicks=0, children=TEXT['end_game'])
                ])
            ])
        ]),
        html.Button(className="modal-close is-large")
    ]),

    bulma_modal(id='waiting', content=TEXT['waiting_for_computer']),

    bulma_modal(id='feedback'),

    bulma_modal(id='intro',
                content=[
                    html.Img(className='header-logo', src='/images/game/{}'.format(GAME_LOGO)),
                    html.Br(), html.Br(),
                    html.Div(TEXT['welcome_header']),
                    html.Ul(children=[
                        html.Li(TEXT['welcome_bullet1']),
                        html.Li(TEXT['welcome_bullet2']),
                        html.Li(TEXT['welcome_bullet3']),
                        html.Li(TEXT['welcome_bullet4'])
                    ])
                ],
                btn_text=TEXT['start_game'],
                btn_class='is-success',
                active=True
                ),

    html.Div(' ', id='spacer')
])


@app.server.route('/images/<path:path>')
def serve_images(path):
    """
    Pass local images to the web server
    """
    root_dir = os.getcwd()
    return flask.send_from_directory(os.path.join(root_dir, 'data/images'), path)


@app.callback(
    Output('intro-modal', 'className'),
    [Input('intro-modal-button', 'n_clicks')]
)
def start_game(_):
    """
    Start a new game with the modal button
    """
    if _ is None or _ == 0:
        return 'modal is-active'
    reset_game()
    return 'modal'


@app.callback(
    Output('output-dummy-2', 'value'),
    [Input(component_id='input-computer-mode', component_property='value')]
)
def set_difficulty(difficulty):
    """
    Set difficulty level with pulldown
    """
    if difficulty == 'hard':
        game.set_computer_mode('best')
    elif difficulty == 'easy':
        game.set_computer_mode('random')
    else:
        pass
    return ''


@app.callback(
    Output(component_id='output-selected-character', component_property='src'),
    [Input(component_id='input-character-select', component_property='value')]
)
def select_character(name):
    """
    Select computer character using pulldown
    """
    if name is None:
        return default_image

    logging.info("Setting computer character to {}".format(name))
    for c in characters:
        if c['name'] == name:
            game.set_computer_character(name)
            return c['file']
    raise ValueError("Character '{}' not found".format(name))


@app.callback(
    Output(component_id='input-question-value', component_property='options'),
    [Input(component_id='input-question-type', component_property='value')]
)
def set_question_options(question_type):
    """
    Fill pulldown options for questions
    """
    if question_type is None:
        return []
    return get_question_value_options(question_type)


@app.callback(
    Output('output-question-answer', 'children'),
    [Input('input-question-button', 'n_clicks')],
    [State('input-question-type', 'value'),
     State('input-question-value', 'value')],
)
def ask_question(_, question_type, question_value):
    """
    Ask a quesiton using the information in the pulldowns
    """
    if _ is None or _ == 0:
        return ''
    logging.info('{}: {}'.format(question_type, question_value))
    ok, answer = get_answer(question_type, question_value)
    if not ok:
        return TEXT['already_moved']
    else:
        return '{}, {} {} {}'.format(
            (TEXT['yes'] if answer else TEXT['no']).capitalize(),
            TEXT[question_type].lower(),
            'is' if answer else 'is {}'.format(TEXT['not']),
            TEXT[question_value]
        )


@app.callback(
    Output('output-hidden-guess', 'accessKey'),
    [Input('input-guess-button', 'n_clicks')],
    [State('input-character-guess', 'value')],
)
def make_guess(_, character_name):
    """
    Guess character selected in pulldown
    """
    if _ is None or _ == 0:
        return ''
    logging.info('Player is guessing for character {}'.format(character_name))
    ok, answer = guess_character(character_name)
    if not ok:
        logging.info("No answer received for guess")
        return '9'
    if answer:
        logging.info("Guess is correct! Player has won!")
        return '1'
    else:
        logging.info("Guess is incorrect")
        return '0'


@app.callback(
    Output('output-hidden-state', 'accessKey'),
    [Input('input-endturn-button', 'n_clicks')]
)
def end_human_turn(_):
    """
    Let computer player make a move and return updated game state to the front-end
    """
    if _ is None or _ == 0:
        return initial_hidden_state
    game.end_turn()
    game_finished, computer_move = game.do_computer_move()
    if game_finished:
        logging.info("Computer has won!")
        reset_game()
    logging.info(computer_move)
    return json.dumps(computer_move)


@app.callback(
    Output('waiting-modal', 'className'),
    [Input('output-hidden-state', 'accessKey')]
)
def close_waiting_modal(_):
    """
    Close the waiting modal once the game state has been updated (computer's turn is finished)
    """
    return 'modal'


@app.callback(
    Output('end-modal', 'className'),
    [Input('end-modal-button', 'n_clicks')]
)
def end_game(_):
    """
    Doesn't really do much since the front-end will reload and the game will be re-initialized
    """
    if _ > 0:
        game.end()

    return 'modal'


if __name__ == '__main__':
    app.run_server(debug=True, port=8123)