#include "ffmpeg_wrapper.h"
#include <QApplication>

int main(int argc, char *argv[])
{
    QApplication a(argc, argv);
    FFMPEG_WRAPPER w;
    w.show();

    return a.exec();
}
