from flask import current_app

from karmalegoweb.src import models


# Return None if the karmalego with the given id does not have a visualization
def karma_lego_to_visualization(karmalego_id):
    visualization = models.Visualization.query.filter_by(KL_id=karmalego_id).first()
    if not visualization:
        return None
    return visualization.id


# Return None if a karmalego with the given id does not exists
def karmalego_to_discretization(karmalego_id):
    karmalego = models.negative_karma_lego.query.filter_by(id=karmalego_id).first()
    if not karmalego:
        return None
    return karmalego.discretization_name


def karmalego_to_dataset_name(karmalego_id):
    discretization_id = karmalego_to_discretization(karmalego_id)
    if discretization_id is None:
        return None
    discretization = models.discretization.query.filter_by(id=discretization_id).first()
    if not discretization:
        current_app.logger.error(
            f"Could not find the discretization {discretization} of the data mining {karmalego_id} in the database"
        )
        return None
    return discretization.dataset_Name
