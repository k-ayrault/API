<?php

namespace App\Service;

use Symfony\Component\Filesystem\Filesystem;

class LogService
{
    private $fileSystem;
    private $logDir;
    private $cheminFichierLog;

    public function __construct(string $logDir, string $nomFichierLog)
    {
        $this->logDir = $logDir;
        $this->fileSystem = new Filesystem();
        if (!$this->fileSystem->exists($this->logDir)) {
            $this->fileSystem->mkdir($this->logDir);
        }
        $date_format = date("d_m_Y_H_i_u");
        $nomFichierLog .= "_${date_format}.txt";
        $this->cheminFichierLog = $this->logDir . "/" . $nomFichierLog;
    }

    function info(string $text) {
        $this->write("[INFO] ${text}");
    }

    function warning(string $text) {
        $this->write("[WARNING] ${text}");
    }

    function danger(string $text) {
        $this->write("[DANGER] ${text}");
    }

    function error(string $text) {
        $this->write("[ERROR] ${text}");
    }

    function nouveauBloc(string $text) {
        $this->write("--DÉBUT ${text}----------------------------------------------------------------------------");
    }

    function finBloc(string $text) {
        $this->write("--FIN ${text}------------------------------------------------------------------------------");
    }

    private function write(string $text) {
        $this->fileSystem->appendToFile($this->cheminFichierLog, $text."\n", true);
    }

}