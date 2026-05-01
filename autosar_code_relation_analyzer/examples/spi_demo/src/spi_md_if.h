#ifndef SPI_MD_IF_H
#define SPI_MD_IF_H

typedef struct {
    int ready_flag;
    int write_index;
} SpiIfStateType;

extern SpiIfStateType Spi_MD_If;
void SpiIf_MainFunction(void);

#endif
