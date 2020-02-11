#include "ffmpeg_wrapper.h"
#include "ui_ffmpeg_wrapper.h"

FFMPEG_WRAPPER::FFMPEG_WRAPPER(QWidget *parent) :
    QMainWindow(parent),
    ui(new Ui::FFMPEG_WRAPPER)
{
    ui->setupUi(this);
}

FFMPEG_WRAPPER::~FFMPEG_WRAPPER()
{
    delete ui;
}
