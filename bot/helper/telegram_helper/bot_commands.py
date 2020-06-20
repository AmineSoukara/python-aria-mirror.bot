class _BotCommands:
    def __init__(self):
        self.StartCommand = 'mars'
        self.MirrorCommand = 'drive'
        self.TarMirrorCommand = 'tar'
        self.CancelMirror = 'delete'
        self.CancelAllCommand = 'cancelall'
        self.ListCommand = 'search'
        self.StatusCommand = 'status'
        self.AuthorizeCommand = 'authorize'
        self.UnAuthorizeCommand = 'unauthorize'
        self.PingCommand = 'ping'
        self.RestartCommand = 'restart'
        self.StatsCommand = 'info'
        self.HelpCommand = 'help'
        self.LogCommand = 'log'
        self.CloneCommand = "clone"
        self.WatchCommand = 'vid'
        self.TarWatchCommand = 'tarvid'

BotCommands = _BotCommands()
