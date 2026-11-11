// RNF-004-03: cómo se calcula cada indicador, tal como lo define la spec 004 (sección 5).

export const EXPLICACIONES = {
  semana:
    'Sesiones terminadas con al menos una serie confirmada, contadas de lunes a domingo. Una sesión cuenta el día en que empezó.',
  meta: 'Una semana cumple si sus sesiones llegan a tu meta de hoy. La meta es opcional, de 1 a 14.',
  grupos:
    'Series confirmadas de esta semana, en el grupo que cada ejercicio tiene hoy en tu catálogo. Los grupos sin series aparecen con 0.',
  records:
    'Tu serie de mayor peso. Si empatan en peso, la de más reps; si siguen empatadas, la primera vez que la lograste. En peso corporal, la de más reps.',
  pesada: 'El mayor peso que levantaste en esa sesión. En peso corporal, las reps de tu mejor serie.',
  volumen: 'Suma de peso × reps de las series confirmadas en esa sesión. En peso corporal, la suma de reps.',
}
